
from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class BookSkuMigrationTests(TransactionTestCase):
    migrate_from = ("store", "0017_book_is_active_book_sku")
    migrate_to = ("store", "0018_populate_book_sku")
    migrate_latest = ("store", "0020_rename_book_product")

    def test_existing_books_receive_sku(self):
        executor = MigrationExecutor(connection)

        try:
            # Return the test database to migration 0017.
            executor.migrate([self.migrate_from])

            old_apps = executor.loader.project_state(
                [self.migrate_from]
            ).apps
            OldBook = old_apps.get_model("store", "Book")

            book_without_sku = OldBook.objects.create(
                name="Existing Book",
                price=Decimal("19.99"),
            )

            book_with_sku = OldBook.objects.create(
                name="Book With SKU",
                price=Decimal("29.99"),
                sku="CUSTOM-001",
            )

            # Apply the data migration.
            executor = MigrationExecutor(connection)
            executor.migrate([self.migrate_to])

            migrated_apps = executor.loader.project_state(
                [self.migrate_to]
            ).apps
            MigratedBook = migrated_apps.get_model("store", "Book")

            updated_book = MigratedBook.objects.get(
                pk=book_without_sku.pk
            )
            preserved_book = MigratedBook.objects.get(
                pk=book_with_sku.pk
            )

            self.assertEqual(
                updated_book.sku,
                f"BOOK-{book_without_sku.pk:06d}",
            )
            self.assertEqual(
                preserved_book.sku,
                "CUSTOM-001",
            )

        finally:
            # Restore the test database to the latest migration.
            MigrationExecutor(connection).migrate(
                [self.migrate_latest]
            )
