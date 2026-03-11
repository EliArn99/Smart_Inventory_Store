from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Banner,
    BlogCategory,
    Book,
    Category,
    Comment,
    Customer,
    Order,
    OrderItem,
    Post,
    Review,
    ShippingAddress,
    WishlistItem,
)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "price", "stock", "category", "is_digital", "image_tag")
    list_editable = ("price", "stock")
    list_filter = ("category", "digital", "stock")
    search_fields = ("name", "author", "description")
    search_help_text = "Търсене по име, автор или описание"
    list_select_related = ("category",)
    ordering = ("name",)
    list_per_page = 25

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="75" style="object-fit: cover;" />',
                obj.image.url,
            )
        return "Няма снимка"

    image_tag.short_description = "Снимка"

    @admin.display(description="Дигитална")
    def is_digital(self, obj):
        return "Да" if obj.digital else "Не"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ("product",)
    extra = 0
    readonly_fields = ("product_name", "product_price")

    @admin.display(description="Продукт")
    def product_name(self, obj):
        return obj.product.name if obj.product else "—"

    @admin.display(description="Цена")
    def product_price(self, obj):
        return f"{obj.product.price} лв." if obj.product else "—"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "date_ordered", "complete", "get_cart_total_display", "transaction_id")
    list_filter = ("complete", "date_ordered")
    search_fields = ("customer__name", "customer__user__username", "transaction_id")
    search_help_text = "Търсене по клиент или transaction ID"
    inlines = (OrderItemInline,)
    readonly_fields = ("get_cart_total_display", "date_ordered")
    list_select_related = ("customer", "customer__user")
    ordering = ("-date_ordered",)
    date_hierarchy = "date_ordered"
    list_per_page = 25

    @admin.display(description="Обща сума")
    def get_cart_total_display(self, obj):
        return f"{obj.get_cart_total} лв."


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "user")
    search_fields = ("name", "email", "user__username")
    list_select_related = ("user",)
    ordering = ("id",)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "order", "city", "state", "zipcode", "date_added")
    search_fields = ("customer__name", "order__id", "city", "zipcode")
    list_filter = ("city", "state", "date_added")
    list_select_related = ("customer", "order")
    ordering = ("-date_added",)
    date_hierarchy = "date_added"


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "added_at")
    search_fields = ("user__username", "book__name")
    list_select_related = ("user", "book")
    ordering = ("-added_at",)
    date_hierarchy = "added_at"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "created_at", "comment")
    list_filter = ("rating", "book")
    search_fields = ("book__name", "user__username", "comment")
    readonly_fields = ("created_at",)
    list_per_page = 20
    list_select_related = ("book", "user")
    ordering = ("-created_at",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "category", "status", "created_on")
    list_filter = ("status", "category")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    list_select_related = ("category", "author")
    ordering = ("-created_on",)
    date_hierarchy = "created_on"


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title",)
    list_editable = ("is_active", "order")
    ordering = ("order",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "post", "created_on", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("content", "user__username", "post__title")
    list_select_related = ("user", "post")
    ordering = ("-created_on",)
    date_hierarchy = "created_on"
    actions = ("approve_comments",)

    @admin.action(description="Одобри избраните коментари")
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
