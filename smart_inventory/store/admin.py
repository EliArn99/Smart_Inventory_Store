from django.contrib import admin
from .models import Product, Customer, Order, OrderItem, ShippingAddress
from django.utils.html import format_html

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'is_low_stock')

    def is_low_stock(self, obj):
        return obj.stock_quantity < 5
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Ниска наличност?'


admin.site.register(Customer)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_ordered', 'complete', 'transaction_id', 'shipping_status')
    list_filter = ('complete',)
    search_fields = ('customer__name', 'transaction_id')

    def shipping_status(self, obj):
        return "Изисква доставка" if obj.shipping else "Дигитален"
    shipping_status.short_description = "Тип доставка"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'date_added')
    search_fields = ('product__name', 'order__id')
    list_filter = ('date_added',)

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'city', 'state', 'zipcode', 'date_added')
    search_fields = ('customer__name', 'order__id', 'address')

