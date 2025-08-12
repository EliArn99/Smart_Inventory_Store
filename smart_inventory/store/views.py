from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from pyexpat.errors import messages

from .forms import CustomUserCreationForm
from .models import Book, Order, OrderItem, Customer, Category, WishlistItem
import json
from .utils import cartData, cookieCart


def store(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    books = Book.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        books = books.filter(category=category)

    data = cartData(request)
    cartItems = data['cartItems']

    context = {
        'books': books,
        'cartItems': cartItems,
        'category': category,
        'categories': categories,
    }
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


# store/views.py

@require_POST
def updateItem(request):
    data = json.loads(request.body)
    bookId = data.get('bookId')
    action = data.get('action')

    book = get_object_or_404(Book, pk=bookId)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=book)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)
        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        cartItems = order.get_cart_items
        return JsonResponse({'cartItems': cartItems}, safe=False)

    else:
        print('User is not authenticated')
        cookieData = cookieCart(request)
        cart = cookieData['cart']

        if action == 'add':
            cart[bookId] = (cart.get(bookId, {'quantity': 0}))['quantity'] + 1
        elif action == 'remove':
            cart[bookId] = (cart.get(bookId, {'quantity': 0}))['quantity'] - 1

        if cart[bookId]['quantity'] <= 0:
            del cart[bookId]

        response = JsonResponse('Item was added', safe=False)
        response.set_cookie('cart', json.dumps(cart))
        return response


def processOrder(request):
    return JsonResponse('Payment submitted..', safe=False)


def get_cart_data(request):
    data = cartData(request)
    data['order']['get_cart_total'] = float(data['order']['get_cart_total'])
    for item in data['items']:
        item['product']['price'] = float(item['product']['price'])
        item['get_total'] = float(item['get_total'])
    return JsonResponse(data, safe=False)


@login_required
def profile_details(request):
    customer = request.user.customer
    orders = customer.order_set.all()

    context = {
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'store/profile_details.html', context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('store:store')

    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    data = cartData(request)
    cartItems = data['cartItems']

    context = {
        'book': book,
        'cartItems': cartItems
    }
    return render(request, 'store/book_detail.html', context)


@login_required
@require_POST
def update_wishlist(request):
    try:
        data = json.loads(request.body)
        book_id = data.get('bookId')
        action = data.get('action')

        if not all([book_id, action]):
            return JsonResponse({'error': 'Missing bookId or action'}, status=400)

        book = Book.objects.get(id=book_id)
        wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, book=book)

        if action == 'add':
            if created:
                message = 'Книгата е добавена в списъка с желания.'
                added = True
            else:
                message = 'Книгата вече е в списъка с желания.'
                added = True
        elif action == 'remove':
            if not created:
                wishlist_item.delete()
                message = 'Книгата е премахната от списъка с желания.'
                added = False
            else:
                message = 'Книгата не е в списъка с желания.'
                added = False
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        return JsonResponse({'message': message, 'added': added, 'book_id': book_id})

    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='login')
def wishlist_view(request):
    user_wishlist = WishlistItem.objects.filter(user=request.user)
    context = {'wishlist_items': user_wishlist}
    return render(request, 'store/wishlist.html', context)
