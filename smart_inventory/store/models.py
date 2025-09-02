from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

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


class Book(models.Model):
    name = models.CharField(max_length=200, null=True)
    author = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.IntegerField(default=0)
    publication_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
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
    product = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        verbose_name = 'Желана книга'
        verbose_name_plural = 'Желани книги'

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.book.name}"


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
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


class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=[(0, "Draft"), (1, "Published")], default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
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
    order = models.IntegerField(default=0, help_text="По-ниското число се показва по-рано")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title




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
#         settings.AUTH_USER_MODEL,
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
#         # Гарантира, че потребителят може да има само един основен списък.
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
#         return f"Книга '{self.book.title}' в '{self.user_list.name}'"


