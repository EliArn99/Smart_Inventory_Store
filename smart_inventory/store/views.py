from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Book, Order, OrderItem, Customer
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
        print("Received data:", data)

        bookId = data.get('bookId')
        action = data.get('action')

        if not bookId or not action:
            return JsonResponse({"error": "Invalid request data: bookId or action missing."}, status=400)

        book = get_object_or_404(Book, pk=bookId)

        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated."}, status=400)

        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = Customer.objects.create(user=request.user, name=request.user.username, email=request.user.email)
            print(f"Created new customer for user: {customer.name}")


        order = Order.objects.filter(customer=customer, complete=False).first()
        if not order:
            order = Order.objects.create(customer=customer, complete=False)
            print(f"Created new order for customer: {customer.name}")

        orderItem, created = OrderItem.objects.get_or_create(order=order, product=book)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)
        else:
            return JsonResponse({"error": "Invalid action specified."}, status=400)

        orderItem.save()
        print(f"OrderItem for {book.name} updated. New quantity: {orderItem.quantity}")

        if orderItem.quantity <= 0:
            orderItem.delete()
            print(f"OrderItem for {book.name} deleted as quantity is 0 or less.")

        # Актуализираме броя на артикулите в количката
        cartItems = order.get_cart_items
        print(f"Cart items after update: {cartItems}")

        return JsonResponse({'cartItems': cartItems}, safe=False)

    except json.JSONDecodeError:
        print("Invalid JSON received.")
        return JsonResponse({"error": "Invalid JSON format in request body."}, status=400)
    except Book.DoesNotExist:
        print(f"Book with ID {bookId} not found.")
        return JsonResponse({"error": f"Book with ID {bookId} not found."}, status=404) # 404 Not Found
    except Exception as e:
        print(f"Error in updateItem view: {e}")
        return JsonResponse({'error': str(e)}, status=500) # 500 Internal Server Error


def processOrder(request):
    return JsonResponse('Payment submitted..', safe=False)


def get_cart_data(request):
    data = cartData(request)
    data['order']['get_cart_total'] = float(data['order']['get_cart_total'])
    for item in data['items']:
        item['product']['price'] = float(item['product']['price'])
        item['get_total'] = float(item['get_total'])
    return JsonResponse(data, safe=False)
