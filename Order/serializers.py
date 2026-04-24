from rest_framework import serializers
from . models import Order , OrderItem

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'delivery_address', 'total_price', 'status', 'order_date']
        read_only_fields = ['customer', 'total_price', 'order_date']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = ['price']

