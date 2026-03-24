from decimal import Decimal

from django.test import TestCase

from ..models import Book, Category, Customer, Order, OrderItem


class OrderModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fantasy", slug="fantasy")
        self.book = Book.objects.create(
            name="The Hobbit",
            price=Decimal("15.00"),
            digital=False,
            category=self.category,
        )
        self.customer = Customer.objects.create(name="Test User", email="test@example.com")
        self.order = Order.objects.create(customer=self.customer, complete=False)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.book,
            quantity=2,
        )

    def test_order_item_get_total(self):
        self.assertEqual(self.order_item.get_total, Decimal("30.00"))

    def test_order_get_cart_total(self):
        self.assertEqual(self.order.get_cart_total, Decimal("30.00"))

    def test_order_get_cart_items(self):
        self.assertEqual(self.order.get_cart_items, 2)

    def test_order_shipping_true_for_non_digital_book(self):
        self.assertTrue(self.order.shipping)