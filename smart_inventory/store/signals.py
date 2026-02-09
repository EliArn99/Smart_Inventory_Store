import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Customer, Book

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Book)
def pre_save_book(sender, instance: Book, **kwargs):

    if instance.pk:
        try:
            instance._old_stock = Book.objects.values_list("stock", flat=True).get(pk=instance.pk)
        except Book.DoesNotExist:
            instance._old_stock = None
    else:
        instance._old_stock = None


@receiver(post_save, sender=get_user_model())
def create_customer_profile(sender, instance, created: bool, **kwargs):

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
def check_low_stock(sender, instance: Book, created: bool, **kwargs):

    alert_email = getattr(settings, "LOW_STOCK_ALERT_EMAIL", None)
    if not alert_email:
        return

    threshold = getattr(settings, "LOW_STOCK_THRESHOLD", 5)

    old_stock = getattr(instance, "_old_stock", None)
    if created or old_stock is None:
        return

    if old_stock > threshold and instance.stock <= threshold:
        subject = f"Предупреждение за ниска наличност: {instance.name}"
        message = (
            f'Наличността на книгата "{instance.name}" от автор {instance.author} '
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
            logger.exception("Грешка при изпращане на имейл за ниска наличност (Book id=%s)", instance.pk)
