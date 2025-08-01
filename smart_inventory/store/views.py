from django.http import JsonResponse
from django.shortcuts import render
from .models import *
import json


# Главна страница на книжарницата.
def store(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'store/store.html', context)


# Страница за количката.
def cart(request):
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    # else:
    #     # Временно решение за нерегистрирани потребители
    #     items = []
    #     order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    #
    # context = {'items': items, 'order': order}
    return render(request, 'store/cart.html')


# Страница за финализиране на поръчката.
def checkout(request):
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    # else:
    #     # Временно решение за нерегистрирани потребители
    #     items = []
    #     order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    #
    # context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html')


# AJAX endpoint за обновяване на продукти в количката.
def updateItem(request):
    data = json.loads(request.body)
    bookId = data['bookId']
    action = data['action']

    print('Action:', action)
    print('Book Id:', bookId)

    customer = request.user.customer
    book = Book.objects.get(id=bookId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=book)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


# AJAX endpoint за обработка на поръчка.
def processOrder(request):
    data = json.loads(request.body)
    # Тук ще се добави логиката за обработка на поръчката.
    # Например: запазване на адреса за доставка, маркиране на поръчката като завършена и т.н.
    return JsonResponse('Payment submitted..', safe=False)
