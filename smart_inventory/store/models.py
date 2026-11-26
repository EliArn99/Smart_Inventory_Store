from uuid import uuid4

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def generate_product_sku():
    return f"PRD-{uuid4().hex.upper()}"


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    icon = models.CharField(
        max_length=50,
        default='fas fa-book',
        help_text="Font Awesome class, e.g., 'fas fa-book'"
    )

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/category/{self.slug}/'


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)

    sku = models.CharField(
        max_length=64,
        unique=True,
        default=generate_product_sku,
        editable=False,
    )

    is_active = models.BooleanField(default=True)

    author = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    stock = models.IntegerField(default=0)
    publication_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            return self.image.url
        except ValueError:
            return ""


class Order(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)

    idempotency_key = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    idempotency_fingerprint = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        editable=False,
    )

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()

        for i in orderitems:
            if i.product.digital is False:
                shipping = True

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
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True
    )
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class WishlistItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    book = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        verbose_name = 'Желана книга'
        verbose_name_plural = 'Желани книги'

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.book.name}"


class Review(models.Model):
    book = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Оценка от 1 до 5 звезди"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        verbose_name = 'Ревю'
        verbose_name_plural = 'Ревюта'

    def __str__(self):
        return f"Ревю от {self.user.username} за {self.book.name}"


class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Blog Categories"

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    content = models.TextField()
    image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts'
    )
    views = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(
        choices=[(0, "Draft"), (1, "Published")],
        default=0
    )

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Коментар от {self.user.username} на {self.post.title}"


class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)
    url = models.URLField(blank=True, null=True)
    order = models.IntegerField(
        default=0,
        help_text="По-ниското число се показва по-рано"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        SALE = "sale", "Продажба"
        RESTOCK = "restock", "Зареждане"
        ADJUSTMENT = "adjustment", "Корекция"

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )

    reason = models.CharField(
        max_length=20,
        choices=Reason.choices,
    )

    quantity_change = models.IntegerField()

    stock_before = models.PositiveIntegerField()
    stock_after = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=["product", "-created_at"],
                name="stock_move_product_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(quantity_change=0),
                name="stock_move_nonzero_qty",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product_id}: "
            f"{self.quantity_change:+d} "
            f"({self.get_reason_display()})"
        )

# TODO: Finish
# class UserListManager(models.Manager):
#
#     def get_main_list(self, user):
#         try:
#             return self.get(user=user, is_main=True)
#         except self.model.DoesNotExist:
#             return None
#
# class UserList(models.Model):
#
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='custom_lists',
#         verbose_name='Потребител'
#     )
#     name = models.CharField(
#         max_length=255,
#         verbose_name='Име на списъка'
#     )
#     is_main = models.BooleanField(
#         default=False,
#         verbose_name='Основен списък'
#     )
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name='Дата на създаване'
#     )
#
#     objects = UserListManager()
#
#     class Meta:
#         verbose_name = 'Потребителски списък'
#         verbose_name_plural = 'Потребителски списъци'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['user'],
#                 condition=models.Q(is_main=True),
#                 name='unique_main_list'
#             )
#         ]
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"Списък '{self.name}' на {self.user.username}"
#
# class UserListItem(models.Model):
#
#     user_list = models.ForeignKey(
#         UserList,
#         on_delete=models.CASCADE,
#         related_name='items',
#         verbose_name='Списък'
#     )
#     book = models.ForeignKey(
#         Book,
#         on_delete=models.CASCADE,
#         verbose_name='Книга'
#     )
#     added_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name='Дата на добавяне'
#     )
#
#     class Meta:
#         verbose_name = 'Елемент от списък'
#         verbose_name_plural = 'Елементи от списъци'
#         unique_together = ('user_list', 'book')
#         ordering = ['-added_at']
#
#     def __str__(self):
#         return f"Книга '{self.book.name}' в '{self.user_list.name}'"
