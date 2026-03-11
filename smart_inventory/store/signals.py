import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Book, Customer

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(pre_save, sender=Book)
def store_previous_book_stock(sender, instance: Book, **kwargs):
    """Store the previous stock value before saving a Book instance."""
    if not instance.pk:
        instance._old_stock = None
        return

    instance._old_stock = (
        Book.objects.filter(pk=instance.pk)
        .values_list("stock", flat=True)
        .first()
    )


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created: bool, **kwargs):
    """Create a Customer profile automatically when a new user is created."""
    if not created:
        return

    Customer.objects.get_or_create(
        user=instance,
        defaults={
            "name": getattr(instance, "username", "") or "",
            "email": getattr(instance, "email", "") or "",
        },
    )


@receiver(post_save, sender=Book)
def send_low_stock_alert(sender, instance: Book, created: bool, **kwargs):
    """Send an email alert when stock drops below the configured threshold."""
    if created:
        return

    alert_email = getattr(settings, "LOW_STOCK_ALERT_EMAIL", "")
    if not alert_email:
        return

    threshold = getattr(settings, "LOW_STOCK_THRESHOLD", 5)
    old_stock = getattr(instance, "_old_stock", None)

    if old_stock is None:
        return

    if old_stock > threshold and instance.stock <= threshold:
        book_name = instance.name or "Неизвестна книга"
        book_author = instance.author or "Неизвестен автор"

        subject = f"Предупреждение за ниска наличност: {book_name}"
        message = (
            f'Наличността на книгата "{book_name}" от автор {book_author} '
            f"е намаляла до {instance.stock} бройки.\n\n"
            f"Моля, поръчайте нови количества."
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[alert_email],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Грешка при изпращане на имейл за ниска наличност (Book id=%s)",
                instance.pk,
            )
