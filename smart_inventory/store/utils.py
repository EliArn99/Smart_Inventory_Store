import json
from .models import Product, Order, OrderItem, Customer


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    # print('CART:', cart) 

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}

    for i in cart:
        try:
            if int(cart[i]['quantity']) > 0:
                product = Product.objects.get(id=i)
                total = (product.price * int(cart[i]['quantity']))  

                order['get_cart_total'] += total
                order['get_cart_items'] += int(cart[i]['quantity']) 

                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'imageURL': product.imageURL,
                    },
                    'quantity': int(cart[i]['quantity']),  # Ensure quantity is int
                    'get_total': total,
                }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
        except Product.DoesNotExist:
            
            print(f"Product with ID {i} not found, skipping.")
            pass
        except Exception as e:
            print(f"Error processing item {i} in cookie cart: {e}")
            pass

    return {'cartItems': order['get_cart_items'], 'order': order, 'items': items}  # Return final get_cart_items


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
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    if created or customer.name != name:
        customer.name = name
        customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item_data in items: # Renamed 'item' to 'item_data' to avoid confusion with OrderItem
        product = Product.objects.get(id=item_data['product']['id']) # Access product ID correctly
        quantity = int(item_data['quantity'])
        if quantity > 0:
            OrderItem.objects.create(
                product=product,
                order=order,
                quantity=quantity,
            )
        else:
            print(f"Skipping order item for product {product.name} due to non-positive quantity: {quantity}")
    return customer, order
