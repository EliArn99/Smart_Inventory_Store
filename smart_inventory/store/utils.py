import json
from .models import Book, Order, OrderItem, Customer # Уверете се, че Customer е импортиран

def cookieCart(request):
    """
    Обработва логиката на количката за неавтентикирани потребители, използвайки бисквитки.
    """
    try:
        # Опитваме се да прочетем и парснем бисквитката 'cart'
        cart_json = request.COOKIES.get('cart')
        if cart_json:
            cart = json.loads(cart_json)
            print('DEBUG (cookieCart): Raw cart cookie:', cart_json) # Дебъг принт за суровата бисквитка
        else:
            cart = {}
            print('DEBUG (cookieCart): Cart cookie not found, initializing empty cart.')
    except json.JSONDecodeError:
        # Ако JSON форматът е невалиден, инициализираме празна количка
        cart = {}
        print('ERROR (cookieCart): Invalid JSON in cart cookie, initializing empty cart.')
    except Exception as e:
        # Обща грешка при четене на бисквитката
        cart = {}
        print(f'ERROR (cookieCart): Unexpected error reading cart cookie: {e}, initializing empty cart.')

    print('DEBUG (cookieCart): Parsed cart dictionary:', cart) # Дебъг принт за парснатата количка

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = 0 # Инициализираме брояч на артикулите в количката

    # Итерираме по копие на ключовете, за да можем безопасно да изтриваме елементи от 'cart' по време на итерацията
    for book_id_str in list(cart.keys()):
        try:
            # Уверяваме се, че количеството е положително
            if cart[book_id_str]['quantity'] > 0:
                quantity = cart[book_id_str]['quantity']
                cartItems += quantity

                # Взимаме продукта от базата данни
                # Уверете се, че book_id_str е преобразуван в int, тъй като ключовете от JSON са стрингове
                product = Book.objects.get(id=int(book_id_str))
                total = (product.price * quantity)

                order['get_cart_total'] += total
                order['get_cart_items'] += quantity

                item = {
                    'id': product.id,
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price), # Уверете се, че цената е float
                        'imageURL': product.imageURL
                    },
                    'quantity': quantity,
                    'digital': product.digital,
                    'get_total': float(total), # Уверете се, че общата сума е float
                }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            else:
                # Ако количеството е 0 или отрицателно, премахваме елемента от количката в бисквитката
                print(f"DEBUG (cookieCart): Removing item {book_id_str} with non-positive quantity from cart.")
                del cart[book_id_str]
        except Book.DoesNotExist:
            # Ако книгата не е намерена в базата данни, премахваме я от бисквитката
            print(f"WARNING (cookieCart): Book with ID {book_id_str} not found in database, removing from cookie cart.")
            del cart[book_id_str]
        except Exception as e:
            # Обща грешка при обработка на конкретен елемент от количката
            print(f"ERROR (cookieCart): Problem processing item {book_id_str} in cookieCart: {e}")
            del cart[book_id_str] # Премахваме проблемния елемент

    print('DEBUG (cookieCart): Final cart items (backend):', cartItems)
    print('DEBUG (cookieCart): Final order (backend):', order)
    print('DEBUG (cookieCart): Final items list (backend):', items)

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    """
    Връща данни за количката в зависимост от това дали потребителят е автентикиран.
    """
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # За неавтентикирани потребители, извикваме cookieCart
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):
    """
    Създава поръчка за потребител гост.
    """
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
        product = Book.objects.get(id=item['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=(item['quantity'] if item['quantity'] > 0 else -1 * item['quantity']),
            # negative quantity = freebies
        )
    return customer, order
