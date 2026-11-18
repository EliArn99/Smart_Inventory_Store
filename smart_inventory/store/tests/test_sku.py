
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from store.models import Product


class BookSkuTests(TestCase):

    def test_sku_is_generated_automatically(self):
        book = Product.objects.create(
            name="Test Product",
            price=Decimal("19.99"),
        )

        self.assertTrue(book.sku)
        self.assertRegex(book.sku, r"^PRD-[0-9A-F]{32}$")

    def test_generated_skus_are_different(self):
        first = Product.objects.create(
            name="First Product",
            price=Decimal("10.00"),
        )

        second = Product.objects.create(
            name="Second Product",
            price=Decimal("20.00"),
        )

        self.assertNotEqual(first.sku, second.sku)

    def test_existing_sku_is_preserved(self):
        book = Product.objects.create(
            name="Old Product",
            price=Decimal("15.00"),
            sku="BOOK-000001",
        )

        book.name = "Updated Product"
        book.save()
        book.refresh_from_db()

        self.assertEqual(book.sku, "BOOK-000001")

    def test_duplicate_sku_is_rejected(self):
        Product.objects.create(
            name="First Product",
            price=Decimal("10.00"),
            sku="TEST-000001",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    name="Second Product",
                    price=Decimal("20.00"),
                    sku="TEST-000001",
                )
