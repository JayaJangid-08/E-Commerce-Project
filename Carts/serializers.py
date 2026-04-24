from rest_framework import serializers
from .models import Cart

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id' , 'product' , 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        return Cart.objects.create(user=user, **validated_data)

