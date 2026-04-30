import json
import logging
from decimal import Decimal

from django.db import transaction

from .models import Book, Customer, Order, OrderItem

logger = logging.getLogger(__name__)


def get_or_create_customer_for_user(user):
    customer, _ = Customer.objects.get_or_create(
        user=user,
        defaults={
            "name": getattr(user, "username", "") or "",
            "email": getattr(user, "email", "") or "",
        },
    )
    return customer


def get_cart_from_cookie(request):
    try:
        return json.loads(request.COOKIES.get("cart", "{}"))
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in cart cookie. Initializing empty cart.")
        return {}
    except Exception:
        logger.exception("Unexpected error while reading cart cookie.")
        return {}


def cookieCart(request):
    cart = get_cart_from_cookie(request)

    items = []
    order = {
        "get_cart_total": Decimal("0.00"),
        "get_cart_items": 0,
        "shipping": False,
    }

    valid_cart = {}

    book_ids = []
    for book_id_str, item_data in cart.items():
        try:
            quantity = int(item_data.get("quantity", 0))
            book_id = int(book_id_str)

            if quantity > 0:
                book_ids.append(book_id)
                valid_cart[str(book_id)] = {"quantity": quantity}
        except (TypeError, ValueError, AttributeError):
            logger.warning("Invalid cart item skipped: %s", book_id_str)

    books = Book.objects.filter(id__in=book_ids).in_bulk()

    for book_id_str, item_data in valid_cart.items():
        book_id = int(book_id_str)
        product = books.get(book_id)

        if not product:
            logger.warning("Book with ID %s not found. Skipping cart item.", book_id)
            continue

        quantity = item_data["quantity"]
        total = product.price * quantity

        order["get_cart_total"] += total
        order["get_cart_items"] += quantity

        items.append(
            {
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "imageURL": product.imageURL,
                    "digital": product.digital,
                    "stock": product.stock,
                },
                "quantity": quantity,
                "get_total": float(total),
            }
        )

        if not product.digital:
            order["shipping"] = True

    return {
        "cartItems": order["get_cart_items"],
        "order": order,
        "items": items,
        "cart": valid_cart,
    }


def cartData(request):
    if request.user.is_authenticated:
        customer = get_or_create_customer_for_user(request.user)

        order, _ = Order.objects.get_or_create(
            customer=customer,
            complete=False,
        )

        items = order.orderitem_set.select_related("product").all()
        cartItems = order.get_cart_items

        return {
            "cartItems": cartItems,
            "order": order,
            "items": items,
        }

    cookieData = cookieCart(request)

    return {
        "cartItems": cookieData["cartItems"],
        "order": cookieData["order"],
        "items": cookieData["items"],
    }


@transaction.atomic
def guestOrder(request, data):
    form_data = data.get("form", {})
    name = form_data.get("name", "").strip()
    email = form_data.get("email", "").strip()

    if not name or not email:
        raise ValueError("Guest order requires name and email.")

    cookieData = cookieCart(request)
    items = cookieData["items"]

    customer, _ = Customer.objects.get_or_create(
        email=email,
        defaults={"name": name},
    )

    if customer.name != name:
        customer.name = name
        customer.save(update_fields=["name"])

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    book_ids = [item["product"]["id"] for item in items]
    books = Book.objects.filter(id__in=book_ids).in_bulk()

    order_items = []

    for item in items:
        product_id = item["product"]["id"]
        product = books.get(product_id)

        if not product:
            logger.warning("Skipping missing product in guest order: %s", product_id)
            continue

        quantity = int(item.get("quantity", 0))

        if quantity <= 0:
            continue

        order_items.append(
            OrderItem(
                product=product,
                order=order,
                quantity=quantity,
            )
        )

    OrderItem.objects.bulk_create(order_items)

    return customer, order
