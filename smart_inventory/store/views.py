from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Book, Order, OrderItem
import json
from .utils import cartData


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    books = Book.objects.all()
    context = {'books': books, 'cartItems': cartItems}
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


@require_POST
def updateItem(request):
    try:
        data = json.loads(request.body)
        bookId = data.get('bookId')
        action = data.get('action')

        if not bookId or not action:
            return HttpResponseBadRequest("Invalid request data.")

        book = get_object_or_404(Book, pk=bookId)

        if not request.user.is_authenticated:
            return HttpResponseBadRequest("User not authenticated.")

        customer = request.user.customer
        # Използваме filter().first() за да вземем най-новата недовършена поръчка
        order = Order.objects.filter(customer=customer, complete=False).first()
        if not order:
            order = Order.objects.create(customer=customer, complete=False)

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

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")
    except Exception as e:
        print(f"Error in updateItem view: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def processOrder(request):
    return JsonResponse('Payment submitted..', safe=False)


def get_cart_data(request):
    data = cartData(request)
    data['order']['get_cart_total'] = float(data['order']['get_cart_total'])
    for item in data['items']:
        item['product']['price'] = float(item['product']['price'])
        item['get_total'] = float(item['get_total'])
    return JsonResponse(data, safe=False)
