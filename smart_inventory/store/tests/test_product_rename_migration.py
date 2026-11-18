
from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class ProductRenameMigrationTests(TransactionTestCase):
    migrate_from = ("store", "0019_alter_book_sku")
    migrate_to = ("store", "0020_rename_book_product")

    def test_rename_preserves_product_and_order_item(self):
        executor = MigrationExecutor(connection)

        try:
            # Start with the old Book model.
            executor.migrate([self.migrate_from])

            old_apps = executor.loader.project_state(
                [self.migrate_from]
            ).apps

            OldBook = old_apps.get_model("store", "Book")
            OldOrder = old_apps.get_model("store", "Order")
            OldOrderItem = old_apps.get_model("store", "OrderItem")

            book = OldBook.objects.create(
                name="Existing Book",
                price=Decimal("25.00"),
                sku="BOOK-000001",
                stock=10,
            )

            order = OldOrder.objects.create()

            order_item = OldOrderItem.objects.create(
                product=book,
                order=order,
                quantity=2,
            )

            # Apply the Book -> Product migration.
            executor = MigrationExecutor(connection)
            executor.migrate([self.migrate_to])

            new_apps = executor.loader.project_state(
                [self.migrate_to]
            ).apps

            Product = new_apps.get_model("store", "Product")
            OrderItem = new_apps.get_model("store", "OrderItem")

            product = Product.objects.get(pk=book.pk)
            updated_item = OrderItem.objects.get(
                pk=order_item.pk
            )

            self.assertEqual(product.name, "Existing Book")
            self.assertEqual(product.sku, "BOOK-000001")
            self.assertEqual(product.stock, 10)
            self.assertEqual(product.price, Decimal("25.00"))

            self.assertEqual(
                updated_item.product_id,
                product.pk,
            )
            self.assertEqual(updated_item.quantity, 2)

        finally:
            # Restore the current migration state.
            MigrationExecutor(connection).migrate(
                [self.migrate_to]
            )
