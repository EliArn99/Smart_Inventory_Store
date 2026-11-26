from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import Product, StockMovement


class ProductStockAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="stock_admin",
            email="stock-admin@example.com",
            password="testpass123",
        )

        cls.product = Product.objects.create(
            name="Test Keyboard",
            price=Decimal("20.00"),
            stock=5,
            digital=True,
            is_active=True,
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def edit_product(self, stock, price="20.00"):
        url = reverse(
            "admin:store_product_change",
            args=[self.product.pk],
        )

        return self.client.post(
            url,
            {
                "name": self.product.name,
                "author": "Test Author",
                "price": price,
                "stock": str(stock),
                "digital": "2",
                "category": "",
                "description": "",
                "publication_year": "",
                "is_active": "on",
                "_save": "Save",
                "sku": self.product.sku,
                "original_stock": str(self.product.stock),
            },
        )

    def test_stock_increase_creates_adjustment(self):
        response = self.edit_product(stock=12)

        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 12)

        movement = StockMovement.objects.get(product=self.product)

        self.assertEqual(
            movement.reason,
            StockMovement.Reason.ADJUSTMENT,
        )
        self.assertEqual(movement.quantity_change, 7)
        self.assertEqual(movement.stock_before, 5)
        self.assertEqual(movement.stock_after, 12)
        self.assertIsNone(movement.order_id)

    def test_price_change_does_not_create_stock_movement(self):
        response = self.edit_product(
            stock=5,
            price="25.00",
        )

        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 5)
        self.assertEqual(self.product.price, Decimal("25.00"))
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_negative_stock_is_rejected(self):
        response = self.edit_product(stock=-3)

        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 5)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_list_editable_creates_stock_movement(self):
        url = reverse("admin:store_product_changelist")

        response = self.client.post(
            url,
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": str(self.product.pk),
                "form-0-price": "20.00",
                "form-0-stock": "3",
                "form-0-is_active": "on",
                "_save": "Save",
                "form-0-original_stock": str(self.product.stock),
            },
        )

        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        movement = StockMovement.objects.get(product=self.product)

        self.assertEqual(
            movement.reason,
            StockMovement.Reason.ADJUSTMENT,
        )
        self.assertEqual(movement.quantity_change, -2)
        self.assertEqual(movement.stock_before, 5)
        self.assertEqual(movement.stock_after, 3)


    def test_stale_admin_form_does_not_restore_sold_stock(self):
        url = reverse(
            "admin:store_product_change",
            args=[self.product.pk],
        )

        # Administrator opens the product with stock=5.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # A checkout happens while the admin form is open.
        Product.objects.filter(pk=self.product.pk).update(stock=3)

        StockMovement.objects.create(
            product=self.product,
            reason=StockMovement.Reason.SALE,
            quantity_change=-2,
            stock_before=5,
            stock_after=3,
        )

        # Administrator edits only the price, using stale stock=5.
        self.edit_product(stock=5, price="25.00")

        self.product.refresh_from_db()

        # A stale form must not restore already sold stock.
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(
            StockMovement.objects.filter(
                reason=StockMovement.Reason.ADJUSTMENT
            ).count(),
            0,
        )


    def test_stale_list_editable_does_not_restore_sold_stock(self):
        url = reverse("admin:store_product_changelist")

        # Admin sees the product with stock=5.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            'name="form-0-original_stock"',
        )

        # A sale reduces stock while the admin page is open.
        Product.objects.filter(pk=self.product.pk).update(stock=3)

        StockMovement.objects.create(
            product=self.product,
            reason=StockMovement.Reason.SALE,
            quantity_change=-2,
            stock_before=5,
            stock_after=3,
        )

        # Admin submits the old stock=5 while changing the price.
        response = self.client.post(
            url,
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": str(self.product.pk),
                "form-0-price": "25.00",
                "form-0-stock": "5",
                "form-0-is_active": "on",
                "form-0-original_stock": "5",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()

        # The stale form must not overwrite the sale.
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.product.price, Decimal("20.00"))

        self.assertEqual(
            StockMovement.objects.filter(
                reason=StockMovement.Reason.ADJUSTMENT
            ).count(),
            0,
        )