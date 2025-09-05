import json
from .models import Book, Order, OrderItem, Customer # Уверете се, че Customer е импортиран

def cookieCart(request):

    try:
        cart_json = request.COOKIES.get('cart')
        if cart_json:
            cart = json.loads(cart_json)
            print('DEBUG (cookieCart): Raw cart cookie:', cart_json) # Дебъг принт за суровата бисквитка
        else:
            cart = {}
            print('DEBUG (cookieCart): Cart cookie not found, initializing empty cart.')
    except json.JSONDecodeError:
        cart = {}
        print('ERROR (cookieCart): Invalid JSON in cart cookie, initializing empty cart.')
    except Exception as e:
        cart = {}
        print(f'ERROR (cookieCart): Unexpected error reading cart cookie: {e}, initializing empty cart.')

    print('DEBUG (cookieCart): Parsed cart dictionary:', cart)

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = 0

    for book_id_str in list(cart.keys()):
        try:
            if cart[book_id_str]['quantity'] > 0:
                quantity = cart[book_id_str]['quantity']
                cartItems += quantity

                product = Book.objects.get(id=int(book_id_str))
                total = (product.price * quantity)

                order['get_cart_total'] += total
                order['get_cart_items'] += quantity

                item = {
                    'id': product.id,
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'imageURL': product.imageURL
                    },
                    'quantity': quantity,
                    'digital': product.digital,
                    'get_total': float(total),
                }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            else:
                print(f"DEBUG (cookieCart): Removing item {book_id_str} with non-positive quantity from cart.")
                del cart[book_id_str]
        except Book.DoesNotExist:
            print(f"WARNING (cookieCart): Book with ID {book_id_str} not found in database, removing from cookie cart.")
            del cart[book_id_str]
        except Exception as e:
            print(f"ERROR (cookieCart): Problem processing item {book_id_str} in cookieCart: {e}")
            del cart[book_id_str]

    # print('DEBUG (cookieCart): Final cart items (backend):', cartItems)
    # print('DEBUG (cookieCart): Final order (backend):', order)
    # print('DEBUG (cookieCart): Final items list (backend):', items)

    return {'cartItems': cartItems, 'order': order, 'items': items}


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
