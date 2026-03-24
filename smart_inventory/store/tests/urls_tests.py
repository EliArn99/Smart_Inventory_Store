from django.test import SimpleTestCase
from django.urls import resolve, reverse

from store import views


class URLTests(SimpleTestCase):
    def test_store_url_is_resolved(self):
        url = reverse("store:store")
        self.assertEqual(resolve(url).func.view_class, views.BookListView)

    def test_cart_url_is_resolved(self):
        url = reverse("store:cart")
        self.assertEqual(resolve(url).func.view_class, views.CartView)

    def test_checkout_url_is_resolved(self):
        url = reverse("store:checkout")
        self.assertEqual(resolve(url).func.view_class, views.CheckoutView)

    def test_about_us_url_is_resolved(self):
        url = reverse("store:about_us")
        self.assertEqual(resolve(url).func.view_class, views.AboutUsView)

    def test_book_detail_url_is_resolved(self):
        url = reverse("store:book_detail", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.BookDetailView)

    def test_blog_list_url_is_resolved(self):
        url = reverse("store:blog_list")
        self.assertEqual(resolve(url).func.view_class, views.BlogListView)

    def test_blog_detail_url_is_resolved(self):
        url = reverse("store:blog_detail", args=["test-slug"])
        self.assertEqual(resolve(url).func.view_class, views.BlogDetailView)

    def test_posts_by_category_url_is_resolved(self):
        url = reverse("store:posts_by_category", args=["test-category"])
        self.assertEqual(resolve(url).func.view_class, views.PostsByCategoryView)

    def test_update_item_url_is_resolved(self):
        url = reverse("store:update_item")
        self.assertEqual(resolve(url).func, views.update_item)

    def test_process_order_url_is_resolved(self):
        url = reverse("store:process_order")
        self.assertEqual(resolve(url).func, views.process_order)

    def test_update_wishlist_url_is_resolved(self):
        url = reverse("store:update_wishlist")
        self.assertEqual(resolve(url).func, views.update_wishlist)