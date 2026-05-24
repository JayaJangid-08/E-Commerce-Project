from rest_framework import serializers
from .models import Warehouse, Inventory, StockMovement, StaffWarehouse

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'
    
    def validate_latitude(self, value):
        if value and (value < -90 or value > 90):
            raise serializers.ValidationError("Invalid latitude")
        return value

    def validate_longitude(self, value):
        if value and (value < -180 or value > 180):
            raise serializers.ValidationError("Invalid longitude")
        return value


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'warehouse', 'warehouse_name', 'product', 'product_name', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity must be greater than or equal to 0")
        return value


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = ['id', 'warehouse', 'warehouse_name', 'product', 'product_name', 'quantity_change', 'reason', 'created_at']
        read_only_fields = ['created_at']


class StaffWarehouseSerializer(serializers.ModelSerializer):
    staff_username = serializers.CharField(source='staff.username', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = StaffWarehouse
        fields = ['id', 'staff', 'staff_username', 'warehouse', 'warehouse_name']