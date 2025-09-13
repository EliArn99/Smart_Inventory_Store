from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Customer, Book


_old_stock = {}

@receiver(pre_save, sender=Book)
def pre_save_book(sender, instance, **kwargs):
    if instance.pk:
        _old_stock[instance.pk] = Book.objects.get(pk=instance.pk).stock


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance, name=instance.username, email=instance.email)


@receiver(post_save, sender=Book)
def check_low_stock(sender, instance, created, **kwargs):
    if not hasattr(settings, 'LOW_STOCK_ALERT_EMAIL'):
        return

    LOW_STOCK_THRESHOLD = 5
    old_stock = _old_stock.get(instance.pk, instance.stock + 1)

    if not created and old_stock > LOW_STOCK_THRESHOLD and instance.stock <= LOW_STOCK_THRESHOLD:
        subject = f'Предупреждение за ниска наличност: {instance.name}'
        message = (
            f'Наличността на книгата "{instance.name}" от автор {instance.author} '
            f'е намаляла до {instance.stock} бройки.\n\n'
            f'Моля, поръчайте нови количества.'
        )

        recipient_list = [settings.LOW_STOCK_ALERT_EMAIL]

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
        except Exception as e:
            print(f"Грешка при изпращане на имейл: {e}")
