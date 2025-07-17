# store/models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Related User Account")
    name = models.CharField(max_length=200, null=True, blank=True, verbose_name="Name")
    email = models.EmailField(max_length=200, unique=True, verbose_name="Email")

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ('email',)

    def __str__(self):
        return self.user.username if self.user else (self.name if self.name else self.email)


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="Category name")
    slug = models.SlugField(max_length=200, unique=True, db_index=True, verbose_name="Short name (slug)")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Image Category")

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])



class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Category")
    name = models.CharField(max_length=200, db_index=True, verbose_name="Product name")
    slug = models.SlugField(max_length=200, unique=True, db_index=True, blank=True, null=True, verbose_name="Short name (slug)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    digital = models.BooleanField(default=False,null=True, blank=True, verbose_name="Digital product")
    image = models.ImageField(null=True, blank=True, upload_to='products/', verbose_name="Product Image")
    stock = models.PositiveIntegerField(default=0, verbose_name="In stock")
    available = models.BooleanField(default=True, verbose_name="In stock for sale")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creation date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last update")

    class Meta:
        ordering = ('name',)
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except ValueError:
            url = ''
        return url

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'pending'),
        ('Processing', 'processing'),
        ('Shipped', 'shipped'),
        ('Delivered', 'delivered'),
        ('Cancelled', 'cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Client")
    date_ordered = models.DateTimeField(auto_now_add=True, verbose_name="Order date")
    complete = models.BooleanField(default=False, verbose_name="Finished")
    transaction_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="Transaction ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Order Status")

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-date_ordered']

    def __str__(self):
        return f"Order {self.id} ({self.status})"

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for item in orderitems:
            if not item.product.digital:
                shipping = True
                break
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Product")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name="Order")
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="Quantity")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Date added")

    class Meta:
        verbose_name = 'Order element'
        verbose_name_plural = 'Order elements'

    def __str__(self):
        return f"{self.product.name} ({self.quantity} units.)"

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name="Client")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name="Order")
    address = models.CharField(max_length=200, null=False, verbose_name="Address")
    city = models.CharField(max_length=200, null=False, verbose_name="City")
    state = models.CharField(max_length=200, null=False, verbose_name="State")
    zipcode = models.CharField(max_length=200, null=False, verbose_name="Postal code")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Date added")

    class Meta:
        verbose_name = 'Delivery Address'
        verbose_name_plural = 'Delivery Addresses'
        ordering = ('-date_added',)

    def __str__(self):
        return self.address


class WishlistItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Client")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")

    class Meta:
        unique_together = ('customer', 'product')
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'

    def __str__(self):
        return f"{self.product.name} in {self.customer.name}'s Wishlist"


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"

