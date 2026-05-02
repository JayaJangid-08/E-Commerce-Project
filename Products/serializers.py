from .models import Product , Category
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

