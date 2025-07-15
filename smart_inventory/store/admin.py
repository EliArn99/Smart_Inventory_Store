from django.utils.html import format_html
from django.contrib import admin
from .models import Customer, Category, Product, Order, OrderItem, ShippingAddress, WishlistItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'email']
    search_fields = ['name', 'email']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'thumbnail_image']
    prepopulated_fields = {'slug': ('name',)}

    def thumbnail_image(self, obj):

        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />'.format(
                    obj.image.url))
        return "-"

    thumbnail_image.short_description = 'Image Preview'  


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'digital', 'created_at', 'thumbnail_image']
    list_filter = ['available', 'digital', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

    def thumbnail_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />'.format(
                    obj.image.url))

        return "-"

    thumbnail_image.short_description = 'Image Preview'  #


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date_ordered', 'complete', 'status', 'transaction_id', 'get_cart_total',
                    'get_cart_items']
    list_filter = ['complete', 'status', 'date_ordered']
    search_fields = ['customer__name', 'transaction_id']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'get_total', 'date_added']
    list_filter = ['date_added']
    search_fields = ['product__name', 'order__id']


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order', 'address', 'city', 'state', 'zipcode', 'date_added']
    list_filter = ['date_added', 'city']
    search_fields = ['customer__name', 'order__id', 'address', 'city']


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product']
    list_filter = ['customer', 'product']
    search_fields = ['customer__name', 'product__name']
