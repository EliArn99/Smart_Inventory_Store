from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

from django.contrib.auth import get_user_model
from django.db import close_old_connections, connections
from django.test import (
    RequestFactory,
    TestCase,
    TransactionTestCase,
    skipUnlessDBFeature,
)

from store.models import Customer, Order, OrderItem, Product
from store.views import process_order


class InventoryTransactionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="inventory_test_user",
            password="testpass123",
        )


        self.customer, _ = Customer.objects.get_or_create(
            user=self.user,
            defaults={
                "name": "Inventory Test",
                "email": "inventory@example.com",
            },
        )


        self.product = Product.objects.create(
            name="Test Product",
            price=Decimal("20.00"),
            stock=3,
            digital=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            complete=False,
        )

        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
        )

        self.factory = RequestFactory()

    def checkout(self):
        request = self.factory.post(
            "/store/process_order/",
            data="{}",
            content_type="application/json",
        )
        request.user = self.user
        return process_order(request)

    def test_successful_order_decreases_stock(self):
        response = self.checkout()

        self.product.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.stock, 1)
        self.assertTrue(self.order.complete)
        self.assertTrue(self.order.transaction_id)

    def test_insufficient_stock_does_not_change_inventory(self):
        self.item.quantity = 5
        self.item.save(update_fields=["quantity"])

        response = self.checkout()

        self.product.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.product.stock, 3)
        self.assertFalse(self.order.complete)

    def test_empty_order_is_rejected(self):
        self.item.delete()

        response = self.checkout()

        self.order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.order.complete)
        self.assertEqual(self.product.stock, 3)

    def test_invalid_quantities_are_rejected(self):
        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                self.item.quantity = quantity
                self.item.save(update_fields=["quantity"])

                response = self.checkout()

                self.product.refresh_from_db()
                self.order.refresh_from_db()

                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.product.stock, 3)
                self.assertFalse(self.order.complete)

    def test_repeated_request_does_not_decrease_stock_twice(self):
        first_response = self.checkout()
        second_response = self.checkout()

        self.product.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(first_response.status_code, 200)
        self.assertIn(second_response.status_code, (400, 409))
        self.assertEqual(self.product.stock, 1)
        self.assertTrue(self.order.complete)
        self.assertEqual(
            Order.objects.filter(customer=self.customer).count(),
            1,
        )



@skipUnlessDBFeature("has_select_for_update")
class ConcurrentCheckoutTests(TransactionTestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Last Available Product",
            price=Decimal("25.00"),
            stock=1,
            digital=True,
        )

        self.users = []
        self.orders = []

        for number in (1, 2):
            user = get_user_model().objects.create_user(
                username=f"concurrent_user_{number}",
                password="testpass123",
            )

            customer, _ = Customer.objects.get_or_create(
                user=user,
                defaults={
                    "name": f"Customer {number}",
                    "email": f"customer{number}@example.com",
                },
            )

            order = Order.objects.create(
                customer=customer,
                complete=False,
            )

            OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=1,
            )

            self.users.append(user)
            self.orders.append(order)

    def test_only_one_order_can_buy_last_item(self):
        barrier = Barrier(2)

        def checkout(user):
            close_old_connections()

            try:
                request = RequestFactory().post(
                    "/store/process_order/",
                    data="{}",
                    content_type="application/json",
                )
                request.user = user

                # Start both checkout requests together.
                barrier.wait(timeout=15)

                response = process_order(request)
                return response.status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(checkout, user)
                for user in self.users
            ]

            statuses = [
                future.result(timeout=30)
                for future in futures
            ]

        self.product.refresh_from_db()

        completed_orders = Order.objects.filter(
            pk__in=[order.pk for order in self.orders],
            complete=True,
        ).count()

        self.assertEqual(sorted(statuses), [200, 400])
        self.assertEqual(self.product.stock, 0)
        self.assertEqual(completed_orders, 1)
