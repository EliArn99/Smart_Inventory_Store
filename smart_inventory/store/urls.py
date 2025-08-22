# store/urls.py

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.store, name="store"),
    path('category/<slug:category_slug>/', views.store, name='books_by_category'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),

    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('search/', views.search_results, name='search_results'),

    path('update_wishlist/', views.update_wishlist, name='update_wishlist'),

    # path('', views.post_list, name='post_list'),
    #
    # path('<slug:slug>/', views.post_detail, name='post_detail'),

    # AJAX endpoint for updating cart items (add/remove)
    path('update_item/', views.updateItem, name="update_item"),

    # AJAX endpoint for processing an order
    path('process_order/', views.processOrder, name="process_order"),
    path('profile/', views.profile_details, name="profile_details"),
    path('register/', views.register, name='register'),

]
