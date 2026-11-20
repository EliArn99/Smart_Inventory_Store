
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import Product


class ProductAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin_user = User.objects.create_superuser(
            username="product_admin_test",
            email="admin@example.com",
            password="testpass123",
        )

        cls.available = Product.objects.create(
            name="Available Product",
            price=Decimal("20.00"),
            stock=15,
        )

        cls.low_stock = Product.objects.create(
            name="Low Stock Product",
            price=Decimal("15.00"),
            stock=3,
        )

        cls.out_of_stock = Product.objects.create(
            name="Out of Stock Product",
            price=Decimal("10.00"),
            stock=0,
        )

        cls.url = reverse("admin:store_product_changelist")

    def setUp(self):
        self.client.force_login(self.admin_user)

    def get_product_ids(self, params):
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, 200)

        products = response.context["cl"].result_list
        return {product.pk for product in products}

    def test_available_stock_filter(self):
        ids = self.get_product_ids({
            "stock_level": "available",
        })

        self.assertEqual(ids, {self.available.pk})

    def test_low_stock_filter(self):
        ids = self.get_product_ids({
            "stock_level": "low",
        })

        self.assertEqual(ids, {self.low_stock.pk})

    def test_out_of_stock_filter(self):
        ids = self.get_product_ids({
            "stock_level": "out",
        })

        self.assertEqual(ids, {self.out_of_stock.pk})

    def test_search_product_by_sku(self):
        ids = self.get_product_ids({
            "q": self.low_stock.sku,
        })

        self.assertEqual(ids, {self.low_stock.pk})

    def test_filter_by_active_status(self):
        self.out_of_stock.is_active = False
        self.out_of_stock.save(update_fields=["is_active"])

        ids = self.get_product_ids({
            "is_active__exact": "0",
        })

        self.assertEqual(ids, {self.out_of_stock.pk})
