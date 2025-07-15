# store/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
import datetime
from .models import Customer, Category, Product, Order, OrderItem, ShippingAddress, WishlistItem
from .utils import cookieCart, cartData, guestOrder  # Ще трябва да създадете utils.py
from django.contrib.auth import login, logout, authenticate

# Импортирайте `csrf_exempt` САМО за тестване! Премахнете го в production.
from django.views.decorators.csrf import csrf_exempt


def store(request, category_slug=None):  # Добавих category_slug, за да може да филтрира по категория
    """
    Основен изглед на магазина, показващ продуктите.
    Сега може да приема category_slug за филтриране.
    """
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.filter(available=True, stock__gt=0)  # Взимаме само налични продукти
    category = None
    categories = Category.objects.all()  # Всички категории за навигация

    if category_slug:
        # Филтрира продукти по конкретна категория, ако е подадена
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'products': products,
        'cartItems': cartItems,
        'categories': categories,  # Добавяме категориите за навигация в шаблона
        'category': category,  # Добавяме текущата категория
    }
    return render(request, 'store/store.html', context)


def product_detail(request, id, slug):
    """
    Изглед за показване на детайлна информация за конкретен продукт.
    """
    data = cartData(request)
    cartItems = data['cartItems']

    product = get_object_or_404(Product, id=id, slug=slug, available=True, stock__gt=0)
    categories = Category.objects.all()  # За да има навигация по категории в base.html

    context = {
        'product': product,
        'cartItems': cartItems,
        'categories': categories,
    }
    return render(request, 'store/detail.html', context)


def cart(request):
    """
    Изглед за страницата на пазарската количка.
    Показва текущите елементи в количката.
    """
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    """
    Изглед за страницата за плащане (checkout).
    Показва обобщение на поръчката и форма за доставка.
    """
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


@csrf_exempt  # !!! ПРЕМАХНЕТЕ ТОВА В PRODUCTION !!!
def updateItem(request):
    """
    AJAX endpoint за актуализиране на количеството на продукт в количката.
    """
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer  # Взимаме свързания Customer обект за текущия потребител
    product = Product.objects.get(id=productId)

    # Взима или създава текущата недовършена поръчка за клиента
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Взима или създава OrderItem за конкретния продукт в тази поръчка
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    # Ако количеството падне до 0 или по-малко, изтриваме елемента от количката
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@csrf_exempt  # !!! ПРЕМАХНЕТЕ ТОВА В PRODUCTION !!!
def processOrder(request):
    """
    AJAX endpoint за обработка на поръчката след потвърждение на плащането.
    """
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        # Логика за гост потребител
        customer, order = guestOrder(request, data)

    # Изчисляваме общата сума от frontend и сравняваме с тази от backend за сигурност
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    # Проверка дали сумата от frontend съвпада с изчислената сума на поръчката
    if total == order.get_cart_total:
        order.complete = True  # Маркира поръчката като завършена
    order.save()

    # Ако поръчката изисква доставка (не е само дигитални продукти)
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            # country=data['shipping']['country'], # Може да добавите и държава, ако я събирате
        )

    return JsonResponse('Payment submitted..', safe=False)


def register_user(request):
    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Customer object for the new user
            Customer.objects.create(user=user, name=user.username, email=user.email)
            login(request, user)
            return redirect('store:store')
    else:
        form = UserCreationForm()

    context = {
        'form': form,
        'cartItems': cartItems,
        'categories': categories,
    }
    return render(request, 'registration/register.html', context)


@login_required(login_url='login')
def user_profile(request):
    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()

    customer_profile = request.user.customer # Get the associated Customer object


    context = {
            'cartItems': cartItems,
            'categories': categories,
            'customer_profile': customer_profile,
            'user': request.user, # The Django User object
        }
    return render(request, 'store/profile.html', context)


@csrf_exempt
@login_required(login_url='login') # Only authenticated users can add/remove from wishlist
def add_to_wishlist(request):
    """
    AJAX endpoint to add or remove a product from the user's wishlist.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('productId')
        action = data.get('action') # 'add_wish' or 'remove_wish'

        if not product_id or not action:
            return JsonResponse({'error': 'Invalid request data'}, status=400)

        customer = request.user.customer
        product = get_object_or_404(Product, id=product_id)

        if action == 'add_wish':
            # Add to wishlist if not already there
            wishlist_item, created = WishlistItem.objects.get_or_create(customer=customer, product=product)
            if created:
                message = 'Product added to wishlist.'
            else:
                message = 'Product already in wishlist.'
            return JsonResponse({'message': message, 'action': 'added'}, status=200)
        elif action == 'remove_wish':
            # Remove from wishlist if it exists
            deleted_count, _ = WishlistItem.objects.filter(customer=customer, product=product).delete()
            if deleted_count > 0:
                message = 'Product removed from wishlist.'
            else:
                message = 'Product not found in wishlist.'
            return JsonResponse({'message': message, 'action': 'removed'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required(login_url='login') # Only authenticated users can view their wishlist
def wishlist_page(request):
    """
    Displays the user's wishlist page.
    """
    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()

    customer = request.user.customer
    wishlist_items = WishlistItem.objects.filter(customer=customer).select_related('product') # Eager load product details

    context = {
        'cartItems': cartItems,
        'categories': categories,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)
