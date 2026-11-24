import json
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from store.models import Customer, Order, OrderItem, Product
from store.views import process_order


class GuestCheckoutReliabilityTests(TestCase):
    def test_out_of_stock_guest_checkout_does_not_create_order(self):
        product = Product.objects.create(
            name="Unavailable Product",
            price=Decimal("10.00"),
            stock=0,
            digital=True,
        )

        request = RequestFactory().post(
            "/store/process_order/",
            data={
                "form": {
                    "name": "Guest Customer",
                    "email": "guest-checkout@example.com",
                }
            },
            content_type="application/json",
        )

        request.user = AnonymousUser()

        request.COOKIES["cart"] = json.dumps(
            {str(product.pk): {"quantity": 1}}
        )

        response = process_order(request)

        self.assertEqual(response.status_code, 400)

        # Failed checkout must not leave an incomplete order.
        self.assertFalse(
            Order.objects.filter(
                customer__email="guest-checkout@example.com"
            ).exists()
        )


    def test_authenticated_checkout_retry_does_not_reduce_stock_twice(self):
        user = get_user_model().objects.create_user(
            username="checkout_retry_user",
            password="testpass123",
        )

        customer, _ = Customer.objects.get_or_create(
            user=user,
            defaults={
                "name": "Checkout Retry User",
                "email": "retry-user@example.com",
            },
        )

        product = Product.objects.create(
            name="Authenticated Checkout Product",
            price=Decimal("25.00"),
            stock=5,
            digital=True,
        )

        order = Order.objects.create(
            customer=customer,
            complete=False,
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
        )

        checkout_key = str(uuid.uuid4())

        def submit_checkout():
            request = RequestFactory().post(
                "/store/process_order/",
                data={
                    "idempotency_key": checkout_key,
                },
                content_type="application/json",
            )
            request.user = user
            return process_order(request)

        first_response = submit_checkout()
        second_response = submit_checkout()

        product.refresh_from_db()
        order.refresh_from_db()

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(product.stock, 3)
        self.assertTrue(order.complete)

        self.assertEqual(
            Order.objects.filter(customer=customer).count(),
            1,
        )

        # Start a genuinely new cart after completing the first order.
        new_order = Order.objects.create(
            customer=customer,
            complete=False,
        )
        OrderItem.objects.create(
            order=new_order,
            product=product,
            quantity=1,
        )

        # Reusing the old key for the new cart must be rejected.
        third_response = submit_checkout()

        product.refresh_from_db()
        new_order.refresh_from_db()

        self.assertEqual(third_response.status_code, 409)
        self.assertEqual(product.stock, 3)
        self.assertFalse(new_order.complete)



    def test_repeated_guest_checkout_creates_only_one_order(self):
        product = Product.objects.create(
            name="Available Product",
            price=Decimal("15.00"),
            stock=3,
            digital=True,
        )

        checkout_key = str(uuid.uuid4())

        def submit_order():
            request = RequestFactory().post(
                "/store/process_order/",
                data={
                    "idempotency_key": checkout_key,
                    "form": {
                        "name": "Repeat Guest",
                        "email": "repeat-guest@example.com",
                    },
                },
                content_type="application/json",
            )

            request.user = AnonymousUser()
            request.COOKIES["cart"] = json.dumps(
                {str(product.pk): {"quantity": 1}}
            )

            return process_order(request)

        first_response = submit_order()
        second_response = submit_order()

        product.refresh_from_db()

        orders = Order.objects.filter(
            customer__email="repeat-guest@example.com"
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(orders.count(), 1)
        self.assertTrue(orders.first().complete)
        self.assertEqual(product.stock, 2)

    def test_empty_guest_cart_does_not_create_order(self):
        request = RequestFactory().post(
            "/store/process_order/",
            data={
                "form": {
                    "name": "Empty Cart Guest",
                    "email": "empty-guest@example.com",
                }
            },
            content_type="application/json",
        )

        request.user = AnonymousUser()

        request.COOKIES["cart"] = json.dumps({})

        response = process_order(request)

        self.assertEqual(response.status_code, 400)

        # An empty guest checkout must not persist an order.
        self.assertFalse(
            Order.objects.filter(
                customer__email="empty-guest@example.com"
            ).exists()
        )

    def test_same_key_with_different_cart_is_rejected(self):
        product = Product.objects.create(
            name="Idempotency Test Product",
            price=Decimal("20.00"),
            stock=3,
            digital=True,
        )

        checkout_key = str(uuid.uuid4())

        def submit_order(quantity):
            request = RequestFactory().post(
                "/store/process_order/",
                data={
                    "idempotency_key": checkout_key,
                    "form": {
                        "name": "Test Guest",
                        "email": "same-key@example.com",
                    },
                },
                content_type="application/json",
            )

            request.user = AnonymousUser()
            request.COOKIES["cart"] = json.dumps(
                {str(product.pk): {"quantity": quantity}}
            )

            return process_order(request)

        first_response = submit_order(1)
        second_response = submit_order(2)

        product.refresh_from_db()

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 409)
        self.assertEqual(product.stock, 2)
        self.assertEqual(
            Order.objects.filter(
                customer__email="same-key@example.com"
            ).count(),
            1,
        )
