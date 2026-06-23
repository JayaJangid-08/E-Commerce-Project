from rest_framework import serializers
from . models import Order , OrderItem , OrderAddress
from Couriers.models import DeliveryAssignment

class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = [ 'id', 'full_name', 'street', 'city', 'state',
                  'pincode', 'latitude', 'longitude', 'phone']


class DeliveryInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAssignment
        fields = ['delivery_status', 'assigned_at', 'delivered_at']

    
class OrderItemSerializer(serializers.ModelSerializer):
    delivery = serializers.SerializerMethodField()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_description', 
                'product_price', 'product_image', 'product_category', 
                'vendor_name', 'quantity', 'status', 'delivery'
            ]
        read_only_fields = ['product_name', 'product_description', 'product_price',
                            'product_image', 'product_category', 'vendor_name'
                        ]
    def get_delivery(self, obj):
        try:
            assignment = obj.delivery_assignment
            return {
                'delivery_status': assignment.delivery_status,
                'assigned_at': assignment.assigned_at,
                'delivered_at': assignment.delivered_at
            }
        except:
            return None  # courier assign nahi hua


class OrderSerializer(serializers.ModelSerializer):
    delivery_address = OrderAddressSerializer(read_only=True)
    # order_items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'delivery_address', 'total_price', 'discount_amount',
                  'final_price', 'status', 'order_date'
                ]
        read_only_fields = ['customer', 'delivery_address', 'discount_amount',
                            'final_price', 'total_price', 'order_date'
                        ]

