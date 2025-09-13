from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Paths for Store and Search
    path('', views.BookListView.as_view(), name='store'),
    path('store/category/<slug:category_slug>/', views.BookListView.as_view(), name='books_by_category'),
    path('search/', views.BookListView.as_view(), name='search_results'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),

    # Paths for Cart and Checkout
    path('cart/', views.CartView.as_view(), name="cart"),
    path('checkout/', views.CheckoutView.as_view(), name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('get_cart_data/', views.get_cart_data, name="get_cart_data"),

    # Paths for Wishlist and User Profile
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('update_wishlist/', views.update_wishlist, name='update_wishlist'),
    path('profile/', views.profile_details, name="profile_details"),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # Paths for Blog
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/category/<slug:category_slug>/', views.PostsByCategoryView.as_view(), name='posts_by_category'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('blog/add/', views.add_post, name='add_post'),

    # General and Administrative Paths
    path('register/', views.register, name='register'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
    path('admin/inventory-report/', views.inventory_report_view, name='inventory_report'),
]
