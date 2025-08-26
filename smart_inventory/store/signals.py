# from django.apps import AppConfig
# from django.core.mail import send_mail
# from django.db.models.signals import post_save
# from django.contrib.auth.models import User
# from django.dispatch import receiver
#
# from django.conf import settings
# from .models import Customer, Book
#
#
# @receiver(post_save, sender=User)
# def create_customer_profile(sender, instance, created, **kwargs):
#     if created:
#         Customer.objects.create(user=instance, name=instance.username)
#
# class StoreConfig(AppConfig):
#     # ...
#     def ready(self):
#         import store.signals
#
#
# @receiver(post_save, sender=Book)
# def check_low_stock(sender, instance, created, **kwargs):
#     LOW_STOCK_THRESHOLD = 5
#
#     if not created and instance.stock <= LOW_STOCK_THRESHOLD and instance.stock > 0:
#         subject = f'Предупреждение за ниска наличност: {instance.name}'
#         message = (
#             f'Наличността на книгата "{instance.name}" от автор {instance.author} '
#             f'е намаляла до {instance.stock} бройки.\n\n'
#             f'Моля, поръчайте нови количества.'
#         )
#
#
#         recipient_list = ['your_email@example.com']
#
#         try:
#             send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
#         except Exception as e:
#             print(f"Грешка при изпращане на имейл: {e}")



from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from .models import Customer, Book

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance, name=instance.username)


@receiver(post_save, sender=Book)
def check_low_stock(sender, instance, created, **kwargs):
    LOW_STOCK_THRESHOLD = 5


    if not created and instance.stock <= LOW_STOCK_THRESHOLD and instance.stock > 0:
        subject = f'Предупреждение за ниска наличност: {instance.name}'
        message = (
            f'Наличността на книгата "{instance.name}" от автор {instance.author} '
            f'е намаляла до {instance.stock} бройки.\n\n'
            f'Моля, поръчайте нови количества.'
        )

        #TODO: Fix here
        # Замени с твоя имейл
        recipient_list = ['eli_arnaytska@abv,bg']

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
        except Exception as e:
            print(f"Грешка при изпращане на имейл: {e}")
