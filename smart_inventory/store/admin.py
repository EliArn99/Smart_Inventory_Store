from django.contrib import admin
from .models import Customer, Book, Order, OrderItem, ShippingAddress

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email')
    search_fields = ('name', 'email')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'price', 'description', 'digital')
    list_filter = ('digital',)
    search_fields = ('name', 'author')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

class ShippingAddressInline(admin.TabularInline):
    model = ShippingAddress
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date_ordered', 'complete', 'transaction_id')
    list_filter = ('complete', 'date_ordered')
    search_fields = ('customer__name', 'transaction_id')
    inlines = [OrderItemInline, ShippingAddressInline]
