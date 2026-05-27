from rest_framework import serializers
from .models import Cart

class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', 
        read_only=True, 
        max_digits=10, 
        decimal_places=2
    )
    product_image = serializers.SerializerMethodField()
    product_category = serializers.CharField(source='product.category.name', read_only=True)
    vendor_name = serializers.CharField(source='product.vendor.username', read_only=True)
    item_total = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'product_category', 'vendor_name', 'quantity', 'item_total']
    
    def get_product_image(self, obj):
        if obj.product.image:
            return str(obj.product.image)
        return None
    
    def get_item_total(self, obj):
        return obj.product.price * obj.quantity

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be greater than 0")
        product = self.initial_data.get('product')
        if product:
            from Products.models import Product
            try:
                prod = Product.objects.get(id=product)
                if value > prod.stock:
                    raise serializers.ValidationError( f"Only {prod.stock} items available in stock")
            except Product.DoesNotExist:
                pass
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        return Cart.objects.create(user=user, **validated_data)

