from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .models import Order , OrderItem
from .serializers import OrderSerializer , OrderItemSerializer
from Authenticate.permissions import IsCustomer , IsAdmin , IsVendor , IsVendorOrAdmin
from Authenticate.models import Address
from Carts.models import Cart

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    if IsCustomer().has_permission(request, None):
        orders = Order.objects.filter(customer=request.user)
    elif IsAdmin().has_permission(request, None):
        orders = Order.objects.all()
    elif IsVendor.has_permission(request, None):
        orders = Order.objects.filter(items__product__vendor=request.user)
    else:
        return Response({'message': 'Permission denied'}, status=403)
    
    paginator = PageNumberPagination()
    paginator.page_size = 5
    paginator_orders = paginator.paginate_queryset(orders , request)
    serializer = OrderSerializer(paginator_orders, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    if not IsCustomer().has_permission(request, None):
        return Response({'message': 'Permission denied'}, status=403)
    
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return Response({'message': 'Cart is empty'}, status=400)
    
    address_id = request.data.get('delivery_address')
    try:
        address = Address.objects.get(id=address_id, user=request.user)
    except Address.DoesNotExist:
        return Response({'message': 'Invalid delivery address'}, status=400)
    
    serializer = OrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        order = serializer.save(customer=request.user)
        total = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            total += item.product.price * item.quantity
        
        order.total_price = total
        order.save()

        cart_items.delete()
        
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'message': 'Order not found'}, status=404)
    
    if IsCustomer().has_permission(request, None):
        if order.customer != request.user:
            return Response({'message': 'Permission denied'}, status=403)
    elif IsVendor().has_permission(request, None):
        if not order.order_items.filter(product__vendor=request.user).exists():
            return Response({'message': 'Permission denied'}, status=403)
    elif not IsAdmin().has_permission(request, None):
        return Response({'message': 'Permission denied'}, status=403)
    
    items = order.order_items.all()
    order_serializer = OrderSerializer(order)
    items_serializer = OrderItemSerializer(items, many=True)
    
    return Response({
        'order': order_serializer.data,
        'items': items_serializer.data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    if not IsCustomer().has_permission(request, None):
        return Response({'message': 'Permission denied'}, status=403)
    
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return Response({'message': 'Order not found'}, status=404)
    
    if order.status == 'shipped' or order.status == 'delivered':
        return Response({'message': 'Order cannot be cancelled'}, status=400)
    
    order.status = 'cancelled'
    order.save()
    return Response({'message': 'Order cancelled successfully'})

# Only admin can update status here
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    if not IsAdmin().has_permission(request, None):
        return Response({'message': 'Permission denied'}, status=403)
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'message': 'Order not found'}, status=404)
    
    new_status = request.data.get('status')
    
    if new_status not in ['confirmed', 'shipped', 'delivered']:
        return Response({'message': 'Invalid status'}, status=400)
    
    if order.status == 'cancelled':
        return Response({'message': 'Cancelled order cannot be updated'}, status=400)
    
    order.status = new_status
    order.save()
    return Response({'message': 'Status updated successfully'})
    
# Only vendor those item are in order can update item status here
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_item_status(request, item_id):
    if not IsVendor().has_permission(request, None):
        return Response({'message': 'Permission denied'}, status=403)
    
    try:
        item = OrderItem.objects.get(id=item_id)
    except OrderItem.DoesNotExist:
        return Response({'message': 'Order not found'}, status=404)
    
    if item.product.vendor != request.user:
        return Response({'message': 'Permission denied'}, status=403)
    
    if item.status in ['delivered', 'cancelled']:
        return Response({'message' : 'Item status cannot be updated'}, status=400)
    
    new_status = request.data.get('status')
    
    if new_status not in ['confirmed', 'shipped', 'delivered']:
        return Response({'message': 'Invalid status'}, status=400)
    
    if item.status == 'cancelled':
        return Response({'message': 'Cancelled order cannot be updated'}, status=400)
    
    item.status = new_status
    item.save()
    return Response({'message': 'Status updated successfully'})
    