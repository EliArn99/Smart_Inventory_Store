
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from store.models import (
    Customer,
    Order,
    OrderItem,
    Product,
    StockMovement,
)
from store.views import process_order


class StockMovementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="stock_movement_user",
            password="testpass123",
        )

        self.customer, _ = Customer.objects.get_or_create(
            user=self.user,
            defaults={
                "name": "Stock Movement User",
                "email": "stock-movement@example.com",
            },
        )

        self.product = Product.objects.create(
            name="Stock Movement Product",
            price=Decimal("20.00"),
            stock=10,
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

    def checkout(self, key=None):
        data = {}

        if key is not None:
            data["idempotency_key"] = key

        request = self.factory.post(
            "/store/process_order/",
            data=data,
            content_type="application/json",
        )
        request.user = self.user

        return process_order(request)

    def test_successful_sale_creates_stock_movement(self):
        response = self.checkout()

        self.product.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.stock, 8)

        movement = StockMovement.objects.get()

        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.order, self.order)
        self.assertEqual(
            movement.reason,
            StockMovement.Reason.SALE,
        )
        self.assertEqual(movement.quantity_change, -2)
        self.assertEqual(movement.stock_before, 10)
        self.assertEqual(movement.stock_after, 8)

    def test_insufficient_stock_creates_no_movement(self):
        self.item.quantity = 15
        self.item.save(update_fields=["quantity"])

        response = self.checkout()

        self.product.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_checkout_retry_does_not_duplicate_movement(self):
        checkout_key = str(uuid.uuid4())

        first_response = self.checkout(checkout_key)
        second_response = self.checkout(checkout_key)

        self.product.refresh_from_db()

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(self.product.stock, 8)
        self.assertEqual(StockMovement.objects.count(), 1)

    def test_duplicate_order_items_create_one_movement(self):
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
        )

        response = self.checkout()

        self.product.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.stock, 5)

        movement = StockMovement.objects.get()

        self.assertEqual(movement.quantity_change, -5)
        self.assertEqual(movement.stock_before, 10)
        self.assertEqual(movement.stock_after, 5)
