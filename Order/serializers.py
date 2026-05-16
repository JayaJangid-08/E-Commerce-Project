from rest_framework import serializers
from . models import Order , OrderItem , OrderAddress

class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = [ 'id', 'full_name', 'street', 'city', 'state', 'pincode', 'latitude', 'longitude', 'phone']


class OrderSerializer(serializers.ModelSerializer):
    delivery_address = OrderAddressSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'delivery_address', 'total_price', 'status', 'order_date']
        read_only_fields = ['customer', 'delivery_address', 'total_price', 'order_date']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = ['price']


