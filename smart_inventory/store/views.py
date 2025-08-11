from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm
from .models import Book, Order, OrderItem, Customer, Category
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

    # Взимаме продукта
    book = get_object_or_404(Book, pk=bookId)

    # Логика за логнат потребител
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

    # Логика за гост
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


@login_required  # Добави този декоратор за защита на страницата
def profile_details(request):
    # Тук можеш да добавиш логика за извличане на данни, свързани с потребителя
    # Например, неговите поръчки или други данни от модела Customer
    customer = request.user.customer
    orders = customer.order_set.all()  # Ако искаш да покажеш история на поръчките

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

    # КОРИГИРАНА ЛОГИКА
    else:  # Ако заявката е GET или формата е невалидна
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


def book_detail(request, pk):
    # Използваме get_object_or_404, за да вземем книгата
    # Ако книга с този ID не съществува, автоматично ще върне 404
    book = get_object_or_404(Book, pk=pk)
    data = cartData(request) # Ако искате да показвате количката и тук
    cartItems = data['cartItems']

    context = {
        'book': book,
        'cartItems': cartItems
    }
    return render(request, 'store/book_detail.html', context)
