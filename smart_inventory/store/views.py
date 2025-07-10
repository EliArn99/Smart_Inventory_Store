from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json
import datetime
from .models import Customer, Category, Product, Order, OrderItem, ShippingAddress  
from .utils import cookieCart, cartData, guestOrder  

from django.views.decorators.csrf import csrf_exempt


def store(request, category_slug=None):  

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.filter(available=True, stock__gt=0)  
    category = None
    categories = Category.objects.all()  

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'products': products,
        'cartItems': cartItems,
        'categories': categories, 
        'category': category,  
    }
    return render(request, 'store/store.html', context)


def product_detail(request, id, slug):

    data = cartData(request)
    cartItems = data['cartItems']

    product = get_object_or_404(Product, id=id, slug=slug, available=True, stock__gt=0)
    categories = Category.objects.all()  

    context = {
        'product': product,
        'cartItems': cartItems,
        'categories': categories,
    }
    return render(request, 'store/detail.html', context)


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


@csrf_exempt  # !!! ПРЕМАХНЕТЕ ТОВА В PRODUCTION !!!
def updateItem(request):

    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer 
    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@csrf_exempt  
def processOrder(request):

    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True  
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            # country=data['shipping']['country'], 
        )

    return JsonResponse('Payment submitted..', safe=False)
