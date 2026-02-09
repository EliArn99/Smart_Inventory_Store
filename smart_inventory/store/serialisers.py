from rest_framework import serializers
from .models import Book, Customer, OrderItem, Order


class BookSerializer(serializers.ModelSerializer):
    imageURL = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'price', 'digital', 'description', 'imageURL']

    def get_imageURL(self, obj):
        request = self.context.get('request')
        if not obj.image:
            return ''
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email']


class OrderItemSerializer(serializers.ModelSerializer):
    product = BookSerializer(read_only=True)
    get_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'get_total']

    def get_get_total(self, obj):
        # safe ако product е None
        return str(obj.get_total) if obj.product else "0.00"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    get_cart_total = serializers.SerializerMethodField()
    get_cart_items = serializers.IntegerField(read_only=True)
    shipping = serializers.BooleanField(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'date_ordered', 'complete', 'transaction_id',
            'get_cart_total', 'get_cart_items', 'shipping', 'items'
        ]

    def get_get_cart_total(self, obj):
        return str(obj.get_cart_total)
