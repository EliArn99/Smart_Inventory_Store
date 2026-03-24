from django.test import TestCase, Client
from django.urls import reverse
import json
from ..models import Book, Customer, Order, OrderItem, Category
from django.contrib.auth.models import User


class StoreViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Fantasy', slug='fantasy')
        self.book1 = Book.objects.create(
            name='The Hobbit',
            price=15.00,
            category=self.category,
            stock=10
        )
        self.book2 = Book.objects.create(
            name='The Lord of the Rings',
            price=30.00,
            category=self.category,
            stock=5
        )
        self.store_url = reverse('store:store')

    def test_store_view_status_code(self):
        # Тестване дали страницата се зарежда успешно
        response = self.client.get(self.store_url)
        self.assertEqual(response.status_code, 200)

    def test_store_view_uses_correct_template(self):
        # Тестване дали се използва правилният шаблон
        response = self.client.get(self.store_url)
        self.assertTemplateUsed(response, 'store/store.html')

    def test_store_view_displays_all_books(self):
        # Тестване дали всички книги се показват на страницата
        response = self.client.get(self.store_url)
        self.assertContains(response, self.book1.name)
        self.assertContains(response, self.book2.name)


    # TODO :FIX
    # def test_store_view_filters_by_category(self):
    #     # Тестване на филтрирането по категория
    #     category_url = reverse('store:books_by_category', args=['fantasy'])
    #     response = self.client.get(category_url)
    #     self.assertContains(response, self.book1.name)
    #     self.assertContains(response, self.book2.name)
    #
    #     other_category = Category.objects.create(name='Fiction', slug='fiction')
    #     other_book = Book.objects.create(name='1984', category=other_category, price=10)
    #
    #     response = self.client.get(category_url)
    #     self.assertNotContains(response, other_book.name)


class BookDetailViewTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(name='Test Book', price=10, stock=1)
        self.detail_url = reverse('store:book_detail', args=[self.book.id])

    def test_book_detail_view_status_code(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_book_detail_view_not_found(self):
        invalid_url = reverse('store:book_detail', args=[99999])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


class UpdateItemViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.customer = Customer.objects.create(user=self.user, name='testuser')
        self.book = Book.objects.create(name='Test Book', price=10, stock=10)
        self.update_url = reverse('store:updateItem')

    def test_update_item_add_action(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(
            self.update_url,
            json.dumps({'bookId': self.book.id, 'action': 'add'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(customer=self.customer, complete=False)
        order_item = OrderItem.objects.get(order=order, product=self.book)
        self.assertEqual(order_item.quantity, 1)

    def test_update_item_remove_action(self):
        self.client.login(username='testuser', password='password123')
        order, _ = Order.objects.get_or_create(customer=self.customer, complete=False)
        order_item = OrderItem.objects.create(order=order, product=self.book, quantity=2)

        response = self.client.post(
            self.update_url,
            json.dumps({'bookId': self.book.id, 'action': 'remove'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        order_item.refresh_from_db()
        self.assertEqual(order_item.quantity, 1)

    def test_update_item_delete_action(self):
        self.client.login(username='testuser', password='password123')
        order, _ = Order.objects.get_or_create(customer=self.customer, complete=False)
        OrderItem.objects.create(order=order, product=self.book, quantity=1)

        response = self.client.post(
            self.update_url,
            json.dumps({'bookId': self.book.id, 'action': 'remove'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(OrderItem.DoesNotExist):
            OrderItem.objects.get(order=order, product=self.book)


class WishlistTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.book = Book.objects.create(name="Test Book", price=10)
        self.wishlist_url = reverse('store:wishlist')

    def test_wishlist_view_authenticated(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/wishlist.html')

    def test_wishlist_view_unauthenticated(self):
        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=' + self.wishlist_url)

class UpdateWishlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.book = Book.objects.create(name="Test Book", price=10, stock=5)
        self.url = reverse("store:update_wishlist")

    def test_add_to_wishlist_authenticated(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            self.url,
            json.dumps({"bookId": self.book.id, "action": "add"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_update_wishlist_requires_login(self):
        response = self.client.post(
            self.url,
            json.dumps({"bookId": self.book.id, "action": "add"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)


class ProcessOrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.customer = Customer.objects.create(user=self.user, name="testuser")
        self.book = Book.objects.create(name="Test Book", price=10, stock=5)
        self.url = reverse("store:process_order")

    def test_process_order_authenticated(self):
        self.client.login(username="testuser", password="password123")
        order = Order.objects.create(customer=self.customer, complete=False)
        OrderItem.objects.create(order=order, product=self.book, quantity=2)

        response = self.client.post(
            self.url,
            json.dumps({
                "form": {"name": "Test User", "email": "test@example.com", "total": "20.00"},
                "shipping": {"address": "Street 1", "city": "Sofia", "state": "Sofia", "zipcode": "1000"},
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.book.refresh_from_db()
        self.assertTrue(order.complete)
        self.assertEqual(self.book.stock, 3)