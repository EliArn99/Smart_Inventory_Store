from django import forms
from django.contrib import admin
from django.db import transaction
from django.utils.html import format_html

from .models import (
    Banner,
    BlogCategory,
    Category,
    Comment,
    Customer,
    Order,
    OrderItem,
    Post,
    Product,
    Review,
    ShippingAddress,
    StockMovement,
    WishlistItem,
)


class StockLevelFilter(admin.SimpleListFilter):
    title = "Складова наличност"
    parameter_name = "stock_level"

    def lookups(self, request, model_admin):
        return (
            ("available", "Налични (над 5)"),
            ("low", "Ниска наличност (1–5)"),
            ("out", "Изчерпани"),
        )

    def queryset(self, request, queryset):
        if self.value() == "available":
            return queryset.filter(stock__gt=5)

        if self.value() == "low":
            return queryset.filter(stock__gte=1, stock__lte=5)

        if self.value() == "out":
            return queryset.filter(stock__lte=0)

        return queryset



class ProductAdminForm(forms.ModelForm):
    stock = forms.IntegerField(
        min_value=0,
        label="Складова наличност",
    )

    original_stock = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput,
    )

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["original_stock"].initial = self.instance.stock

    def clean(self):
        cleaned_data = super().clean()

        if not self.instance.pk:
            return cleaned_data

        original_stock = cleaned_data.get("original_stock")

        if original_stock is None:
            raise forms.ValidationError(
                "Липсва началната наличност. Презаредете страницата."
            )

        current_stock = (
            Product.objects.select_for_update()
            .values_list("stock", flat=True)
            .get(pk=self.instance.pk)
        )

        if current_stock != original_stock:
            raise forms.ValidationError(
                "Наличността е променена от друга операция. "
                "Презаредете страницата и опитайте отново."
            )

        return cleaned_data





@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "author",
        "price",
        "stock",
        "category",
        "is_active",
        "is_digital",
        "image_tag",
    )
    list_editable = ("price", "stock", "is_active")
    list_filter = ("category", "digital", "is_active", StockLevelFilter)
    search_fields = ("name", "sku", "author", "description")
    search_help_text = "Търсене по име, SKU, автор или описание"
    list_select_related = ("category",)
    ordering = ("name",)
    list_per_page = 25
    change_list_template = "store/change_list.html"


    form = ProductAdminForm

    def get_changelist_form(self, request, **kwargs):
        return ProductAdminForm


    def changelist_view(self, request, extra_context=None):
        if request.method == "POST" and "_save" in request.POST:
            with transaction.atomic():
                return super().changelist_view(
                    request,
                    extra_context=extra_context,
                )

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )


    @transaction.atomic
    def save_model(self, request, obj, form, change):
        # Read the current stock while holding a database lock.
        if change:
            stock_before = (
                Product.objects
                .select_for_update()
                .values_list("stock", flat=True)
                .get(pk=obj.pk)
            )
        else:
            stock_before = 0

        # Save the product using Django Admin's normal behavior.
        super().save_model(request, obj, form, change)

        stock_after = obj.stock
        quantity_change = stock_after - stock_before

        # No audit record is needed when stock did not change.
        if quantity_change == 0:
            return

        StockMovement.objects.create(
            product=obj,
            reason=StockMovement.Reason.ADJUSTMENT,
            quantity_change=quantity_change,
            stock_before=stock_before,
            stock_after=stock_after,
        )


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
    list_display = (
        "id",
        "customer",
        "date_ordered",
        "complete",
        "get_cart_total_display",
        "transaction_id",
    )
    list_filter = ("complete", "date_ordered")
    search_fields = (
        "customer__name",
        "customer__user__username",
        "transaction_id",
    )
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
    list_display = (
        "id",
        "customer",
        "order",
        "city",
        "state",
        "zipcode",
        "date_added",
    )
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




@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "product",
        "reason",
        "quantity_change",
        "stock_before",
        "stock_after",
        "order",
    )

    list_filter = (
        "reason",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "order__id",
    )

    list_select_related = (
        "product",
        "order",
    )

    readonly_fields = (
        "product",
        "order",
        "reason",
        "quantity_change",
        "stock_before",
        "stock_after",
        "created_at",
    )

    ordering = ("-created_at", "-pk")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
