from rest_framework import serializers
from . models import Order , OrderItem , OrderAddress

class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = [ 'id', 'full_name', 'street', 'city', 'state',
                  'pincode', 'latitude', 'longitude', 'phone']

    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_description', 
                'product_price', 'product_image', 'product_category', 
                'vendor_name', 'quantity', 'status'
            ]
        read_only_fields = ['product_name', 'product_description', 'product_price',
                            'product_image', 'product_category', 'vendor_name'
                        ]


class OrderSerializer(serializers.ModelSerializer):
    delivery_address = OrderAddressSerializer(read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'delivery_address', 'total_price', 'discount_amount',
                  'final_price', 'status', 'order_date', 'order_items'
                ]
        read_only_fields = ['customer', 'delivery_address', 'discount_amount',
                            'final_price', 'total_price', 'order_date'
                        ]

