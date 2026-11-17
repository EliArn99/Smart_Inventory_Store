
from django.db import migrations
from django.db.models import Q


def populate_book_sku(apps, schema_editor):
    Book = apps.get_model("store", "Book")
    db_alias = schema_editor.connection.alias

    books = (
        Book.objects.using(db_alias)
        .filter(Q(sku__isnull=True) | Q(sku=""))
        .order_by("pk")
    )

    for book in books.iterator():
        sku = f"BOOK-{book.pk:06d}"

        conflict = (
            Book.objects.using(db_alias)
            .filter(sku=sku)
            .exclude(pk=book.pk)
            .exists()
        )

        if conflict:
            raise ValueError(
                f"SKU conflict for Book ID {book.pk}: {sku}"
            )

        Book.objects.using(db_alias).filter(pk=book.pk).update(
            sku=sku
        )


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0017_book_is_active_book_sku"),
    ]

    operations = [
        migrations.RunPython(
            populate_book_sku,
            migrations.RunPython.noop,
        ),
    ]
