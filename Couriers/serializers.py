from rest_framework import serializers
from .models import CourierProfile , DeliveryAssignment


class CourierProfileSerializer(serializers.ModelSerializer):
    delivery_person = serializers.ReadOnlyField(source='delivery_person.username')
    average_rating = serializers.SerializerMethodField()
    class Meta:
        model = CourierProfile
        fields = ['id', 'delivery_person', 'phone_no', 'vehicle_type', 'vehicle_no', 'is_available', 'is_verified', 'average_rating']
        read_only_fields = ['id', 'delivery_person', 'is_verified', 'average_rating']
    
    def get_average_rating(self, obj):
        from django.db.models import Avg
        result = obj.courier_reviews.aggregate(avg=Avg('rating'))['avg']
        return round(result, 2) if result else None


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    courier_name = serializers.CharField(source='courier.delivery_person.username', read_only=True)
    order_item_detail = serializers.SerializerMethodField()
    class Meta:
        model = DeliveryAssignment
        fields = ['id', 'courier', 'courier_name', 'order_item', 'delivery_status', 'assigned_at', 'order_item_detail', 'delivered_at']
        read_only_fields = ['assigned_at', 'delivered_at']

    def get_order_item_detail(self, obj):
        return {
            'product_name': obj.order_item.product_name,
            'product_image': obj.order_item.product_image,
            'quantity': obj.order_item.quantity,
            'customer': obj.order_item.order.customer.username,
            'delivery_address': {
                'street': obj.order_item.order.delivery_address.street,
                'city': obj.order_item.order.delivery_address.city,
                'state': obj.order_item.order.delivery_address.state,
                'pincode': obj.order_item.order.delivery_address.pincode,
                'phone': obj.order_item.order.delivery_address.phone
            }
        }

