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

    # URL for product list filtered by category
    # The 'store' view will handle this, so we point to it.
    path('category/<slug:category_slug>/', views.store, name='product_list_by_category'),

    # URL for a single product's detail page
    # This still points to product_detail view.
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add_to_wishlist/', views.add_to_wishlist, name="add_to_wishlist"),
    path('wishlist/', views.wishlist_page, name="wishlist"),
    path('update_wishlist/', views.updateWishlist, name='update_wishlist'),  # For AJAX requests

]
