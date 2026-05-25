from .models import Product , Category
from rest_framework import serializers
from Reviews.serializers import ReviewSerializer

class ProductSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)
    reviews = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

    def get_reviews(self, obj):
        request = self.context.get('request')

        # detail page only
        if request and request.method == "GET" and "product_id" in request.parser_context.get("kwargs", {}):
            return ReviewSerializer(obj.reviews.all(), many=True).data

        return None

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

