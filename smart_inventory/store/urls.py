# store/urls.py

from django.urls import path
from . import views

app_name = 'store'  # Namespace for the app

urlpatterns = [
    path('', views.store, name="store"),

    path('cart/', views.cart, name="cart"),

    path('checkout/', views.checkout, name="checkout"),

    # AJAX endpoint for updating cart items (add/remove)
    path('update_item/', views.updateItem, name="update_item"),

    # AJAX endpoint for processing an order
    path('process_order/', views.processOrder, name="process_order"),

]
