from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from Products.models import Product
from Authenticate.models import User
from .models import Warehouse, Inventory, StockMovement, StaffWarehouse
from .serializers import WarehouseSerializer, InventorySerializer, StockMovementSerializer
from Authenticate.permissions import IsAdmin, IsAdminOrAssignedStaff

# Create your views here.

def get_user_warehouses(user):
    """Get all warehouses assigned to a user"""
    return Warehouse.objects.filter(staffwarehouse__staff=user)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def assign_warehouse_to_staff(request):
    staff_id = request.data.get('staff')
    warehouse_id = request.data.get('warehouse')
    try:
        staff = User.objects.get(id=staff_id)
    except User.DoesNotExist:
        return Response({'message': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
    try:
        warehouse = Warehouse.objects.get(id=warehouse_id)
    except Warehouse.DoesNotExist:
        return Response({'message': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if already assigned
    if StaffWarehouse.objects.filter(staff=staff, warehouse=warehouse).exists():
        return Response({'message': 'Already assigned'}, status=status.HTTP_400_BAD_REQUEST)
    
    StaffWarehouse.objects.create(staff=staff, warehouse=warehouse)
    return Response({"message" : "Assigned successfully"}, status=status.HTTP_201_CREATED)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def warehouse_list(request):
    if request.method == 'GET':
        warehouse = Warehouse.objects.all()
        serializer = WarehouseSerializer(warehouse, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PATCH','DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def warehouse_detail(request, warehouse_id):
    try:
        warehouse = Warehouse.objects.get(id = warehouse_id)
    except Warehouse.DoesNotExist:
        return Response({'message' : 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = WarehouseSerializer(warehouse)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = WarehouseSerializer(warehouse, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        warehouse.delete()
        return Response({'message' : 'Warehouse Deleted successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrAssignedStaff])
def inventory_list(request):
    if request.user.roles.filter(name='admin').exists():
        inventory = Inventory.objects.all()
    else:
        user_warehouses = get_user_warehouses(request.user)
        inventory = Inventory.objects.filter(warehouse__in=user_warehouses)
    serializer = InventorySerializer(inventory, many=True)
    return Response(serializer.data)


@api_view(['GET','DELETE'])
@permission_classes([IsAuthenticated, IsAdminOrAssignedStaff])
def inventory_detail(request, inventory_id):
    try:
        inventory = Inventory.objects.get(id = inventory_id)
    except Inventory.DoesNotExist:
        return Response({'message' : 'Inventory not found'}, status=status.HTTP_404_NOT_FOUND)

    permission = IsAdminOrAssignedStaff()
    if not permission.has_object_permission(request, None, inventory):
        return Response({'message': 'Only Assigned User and Admin can access'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = InventorySerializer(inventory)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        # Only admin can delete inventory
        if not request.user.roles.filter(name='admin').exists():
            return Response({'message': 'Only Admin can delete inventory'}, status=status.HTTP_403_FORBIDDEN)
        inventory.delete()
        return Response({'message': 'Inventory deleted successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrAssignedStaff])
def stock_movement_list(request):
    if request.user.roles.filter(name='admin').exists():
        stock_movement = StockMovement.objects.all()
    else:
        user_warehouses = get_user_warehouses(request.user)
        stock_movement = StockMovement.objects.filter(warehouse__in=user_warehouses)
    serializer = StockMovementSerializer(stock_movement, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrAssignedStaff])
def stock_movement_detail(request, stock_movement_id):
    try:
        stock_movement = StockMovement.objects.get(id=stock_movement_id)
    except StockMovement.DoesNotExist:
        return Response({'message' : 'Stock history not found'}, status=status.HTTP_404_NOT_FOUND)
    permission = IsAdminOrAssignedStaff()
    if not permission.has_object_permission(request, None, stock_movement):
        return Response({'message': 'Only Assigned User and Admin can access'}, status=status.HTTP_403_FORBIDDEN)
    serializer = StockMovementSerializer(stock_movement)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrAssignedStaff])
def inventory_of_single_warehouse(request, warehouse_id):
    try:
        warehouse = Warehouse.objects.get(id=warehouse_id)
    except Warehouse.DoesNotExist:
        return Response({'message': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)
    
    permission = IsAdminOrAssignedStaff()
    if not permission.has_object_permission(request, None, warehouse):
        return Response({'message': 'Only Assigned User and Admin can access'}, status=status.HTTP_403_FORBIDDEN)
    inventory = Inventory.objects.filter(warehouse=warehouse)
    serializer = InventorySerializer(inventory, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrAssignedStaff])
def stock_history_of_warehouse(request, warehouse_id):
    try:
        warehouse = Warehouse.objects.get(id=warehouse_id)
    except Warehouse.DoesNotExist:
        return Response({'message' : 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)
    
    permission = IsAdminOrAssignedStaff()
    if not permission.has_object_permission(request, None, warehouse):
        return Response({'message': 'Only Assigned User and Admin can access'}, status=status.HTTP_403_FORBIDDEN)
    stock_movement = StockMovement.objects.filter(warehouse=warehouse).order_by('-created_at')
    serializer = StockMovementSerializer(stock_movement, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrAssignedStaff])
def add_stock_in_warehouse(request, warehouse_id):
    try:
        warehouse = Warehouse.objects.get(id=warehouse_id)
    except Warehouse.DoesNotExist:
        return Response({'message': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)
    permission = IsAdminOrAssignedStaff()
    if not permission.has_object_permission(request, None, warehouse):
        return Response({'message': 'Only Assigned User and Admin can access'}, status=status.HTTP_403_FORBIDDEN)
    product_id = request.data.get('product')
    quantity = request.data.get('quantity')
    reason = request.data.get('reason')
    if not product_id or not quantity or not reason:
        return Response({'message' : 'Product, quantity and reason are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response({'message': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'message': 'Quantity must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'message' : 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        inventory, create = Inventory.objects.select_for_update().get_or_create(warehouse=warehouse, product=product, defaults={'quantity':0})
        inventory.quantity += quantity
        inventory.save()
        stock_movement = StockMovement.objects.create(warehouse=warehouse, product=product, quantity_change=quantity, reason=reason)
    serializer = StockMovementSerializer(stock_movement)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrAssignedStaff])
def remove_stock_from_warehouse(request, warehouse_id):
    try:
        warehouse = Warehouse.objects.get(id=warehouse_id)
    except Warehouse.DoesNotExist:
        return Response({'message': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)
    permission = IsAdminOrAssignedStaff()
    if not permission.has_object_permission(request, None, warehouse):
        return Response({'message': 'Only Assigned User and Admin can access'}, status=status.HTTP_403_FORBIDDEN)
    product_id = request.data.get('product')
    quantity = request.data.get('quantity')
    reason = request.data.get('reason')
    if not product_id or not quantity or not reason:
        return Response({'message' : 'Product, quantity and reason are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response({'message': 'Quantity must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'message': 'Quantity must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'message' : 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        try:
            inventory = Inventory.objects.select_for_update().get(warehouse=warehouse, product=product)
        except Inventory.DoesNotExist:
            return Response({'message' : 'Inventory not Found'}, status=status.HTTP_404_NOT_FOUND)
        if inventory.quantity < quantity:
            return Response({'message' : 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        inventory.quantity -= quantity
        inventory.save()
        stock_movement = StockMovement.objects.create(warehouse=warehouse, product=product, quantity_change= -quantity, reason=reason)
    serializer = StockMovementSerializer(stock_movement)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

