import json
from decimal import Decimal
from .models import Book, Order, OrderItem, Customer

def cookieCart(request):

    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except json.JSONDecodeError:
        cart = {}
        print('ERROR (cookieCart): Invalid JSON in cart cookie, initializing empty cart.')
    except Exception as e:
        cart = {}
        print(f'ERROR (cookieCart): Unexpected error reading cart cookie: {e}, initializing empty cart.')

    items = []
    order = {'get_cart_total': Decimal(0), 'get_cart_items': 0, 'shipping': False}
    cartItems = 0
    items_to_delete = []

    for book_id_str, item_data in cart.items():
        try:
            quantity = item_data.get('quantity', 0)
            if quantity > 0:
                product = Book.objects.get(id=int(book_id_str))
                total = product.price * quantity

                order['get_cart_total'] += total
                order['get_cart_items'] += quantity

                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'imageURL': product.imageURL
                    },
                    'quantity': quantity,
                    'get_total': float(total),
                }
                items.append(item)

                if not product.digital:
                    order['shipping'] = True
            else:
                items_to_delete.append(book_id_str)

        except Book.DoesNotExist:
            print(f"WARNING (cookieCart): Book with ID {book_id_str} not found in database, removing from cookie cart.")
            items_to_delete.append(book_id_str)
        except Exception as e:
            print(f"ERROR (cookieCart): Problem processing item {book_id_str} in cookieCart: {e}")
            items_to_delete.append(book_id_str)

    for book_id_str in items_to_delete:
        if book_id_str in cart:
            del cart[book_id_str]

    return {'cartItems': order['get_cart_items'], 'order': order, 'items': items}


def cartData(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):

    print("User is not authenticated")
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Book.objects.get(id=item['product']['id'])
        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )
    return customer, order
