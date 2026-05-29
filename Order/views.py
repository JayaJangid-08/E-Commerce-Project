from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.pagination import PageNumberPagination

from .models import Order , OrderItem , OrderAddress
from Carts.serializers import CartSerializer
from .models import StatusChoice
from .serializers import OrderSerializer , OrderItemSerializer , OrderAddressSerializer
from Authenticate.permissions import IsCustomer , IsAdmin , IsVendor , IsVendorOrAdmin
from .services.pricing import apply_pricing , build_items_from_cart , get_eligible_items , calculate_discount
from Discount.models import Discount
from Authenticate.models import Address
from Carts.models import Cart


# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    if IsCustomer().has_permission(request, None):
        orders = Order.objects.filter(customer=request.user).order_by('-order_date')
    elif IsAdmin().has_permission(request, None):
        orders = Order.objects.all().order_by('-order_date')
    elif IsVendor().has_permission(request, None):
        orders = Order.objects.filter(order_items__product__vendor=request.user).order_by('-order_date')
    else:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    paginator = PageNumberPagination()
    paginator.page_size = 5
    paginator_orders = paginator.paginate_queryset(orders , request)
    serializer = OrderSerializer(paginator_orders, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated , IsCustomer])
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user) 
    
    if not cart_items.exists():
        return Response({'message': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get selected cart item IDs from request
    cart_item_ids = request.data.get('cart_item_ids', [])
    if isinstance(cart_item_ids, int):
            cart_item_ids = [cart_item_ids]
    if not cart_item_ids:
            return Response({'message': 'Please select at least one item from cart'}, status=status.HTTP_400_BAD_REQUEST)
    # Get ONLY selected cart items
    cart_items = Cart.objects.filter(id__in=cart_item_ids, user=request.user)
    if not cart_items.exists():
            return Response({'message': 'No valid cart items selected'},  status=status.HTTP_400_BAD_REQUEST)
    # Frontend sends address_id
    address_id = request.data.get('address_id')
    coupon_name = request.data.get('coupon')
    try:
        address = Address.objects.get(id=address_id, user=request.user)
    except Address.DoesNotExist:
        return Response({'message': 'Invalid delivery address'}, status=status.HTTP_400_BAD_REQUEST)

    items = build_items_from_cart(cart_items)
    pricing = apply_pricing(items, coupon_name)
    if pricing.get("error"):
        return Response({'message': pricing['error']}, status=status.HTTP_400_BAD_REQUEST)
    coupon = pricing.get("coupon_obj")

    for item in cart_items:
        if item.product.stock < item.quantity:
            return Response({'message':f'Insufficient stock for {item.product.name}'}, status=status.HTTP_400_BAD_REQUEST)    
    
    with transaction.atomic():
        order_address = OrderAddress.objects.create(
            full_name=request.user.username,
            street=address.street,
            city=address.city,
            state=address.state,
            pincode=address.pincode,
            latitude=address.latitude,
            longitude=address.longitude,
            phone=address.phone
        )
        order = Order.objects.create(
            customer=request.user,
            delivery_address=order_address,
            total_price=pricing['subtotal'],
            discount_amount=pricing['discount_amount'],
            final_price=pricing['final_price']
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_description=item.product.description,
                product_price=item.product.price,
                product_image=str(item.product.image),
                product_category=item.product.category.name if item.product.category else 'N/A',
                vendor_name=item.product.vendor.username if item.product.vendor else 'N/A',
                quantity=item.quantity
            )
            item.product.stock -= item.quantity
            item.product.save()
        
        if coupon:
            coupon.used_count += 1
            coupon.save()
        
        cart_items.delete() 
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if IsCustomer().has_permission(request, None):
        if order.customer != request.user:
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    elif IsVendor().has_permission(request, None):
        if not order.order_items.filter(product__vendor=request.user).exists():
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    elif not IsAdmin().has_permission(request, None):
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    items = order.order_items.all()
    order_serializer = OrderSerializer(order)
    items_serializer = OrderItemSerializer(items, many=True)
    
    return Response({
        'order': order_serializer.data,
        'items': items_serializer.data
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsCustomer])
def cancel_order_item(request, item_id): 
    try:
        item = OrderItem.objects.get(id=item_id, order__customer=request.user)
    except OrderItem.DoesNotExist:
        return Response({'message': 'Order item not found'}, status=status.HTTP_404_NOT_FOUND)
    if item.status in ['shipped', 'delivered']:
        return Response({'message': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    if item.status == 'cancelled':
        return Response({'message': 'Cancelled order cannot be cancel again'}, status=status.HTTP_400_BAD_REQUEST)

    item.status = 'cancelled'
    item.save()
    return Response({'message': 'Order item cancelled successfully'}, status=status.HTTP_200_OK)


VALID_ITEM_STATUSES = [
    StatusChoice.CONFIRMED,
    StatusChoice.SHIPPED,
    StatusChoice.DELIVERED,
]
# Only admin can update order status here
@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdmin])
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    if new_status not in VALID_ITEM_STATUSES:
        return Response({'message': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    if order.status == StatusChoice.CANCELLED:
        return Response({'message': 'Cancelled order cannot be updated'}, status=status.HTTP_400_BAD_REQUEST)
    
    order.status = new_status
    order.save()
    return Response({'message': 'Status updated successfully'})


# Only vendor whose item is in order can update item status here
@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsVendor])
def update_item_status(request, item_id):
    try:
        item = OrderItem.objects.get(id=item_id)
    except OrderItem.DoesNotExist:
        return Response({'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not item.product or item.product.vendor != request.user:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if item.status in [StatusChoice.DELIVERED, StatusChoice.CANCELLED]:
        return Response({'message' : 'Item status cannot be updated'}, status=status.HTTP_400_BAD_REQUEST)
    
    new_status = request.data.get('status')
    if new_status not in VALID_ITEM_STATUSES:
        return Response({'message': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    item.status = new_status
    item.save()
    return Response({'message': 'Status updated successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def preview_order(request):
    try:
        cart_item_ids = request.query_params.get('cart_item_ids', '')
        coupon_name = request.query_params.get('coupon')
        if cart_item_ids:
            # Selected items (convert string to list)
            try:
                cart_item_ids = [int(id) for id in cart_item_ids.split(',')]
            except ValueError:
                return Response({'message': 'Invalid cart_item_ids format'},  status=status.HTTP_400_BAD_REQUEST)
            cart_items = Cart.objects.filter(id__in=cart_item_ids, user=request.user)
        else:
            # All cart items
            cart_items = Cart.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return Response({'message': 'Cart is empty'},  status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate pricing
        items = build_items_from_cart(cart_items)
        pricing = apply_pricing(items, coupon_name)
        
        if pricing.get("error"):
            return Response({'message': pricing['error']},  status=status.HTTP_400_BAD_REQUEST)
        
        # Add cart items details
        pricing['selected_items'] = CartSerializer(cart_items, many=True).data
        pricing['total_items'] = cart_items.count()
        
        return Response(pricing, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'message': 'Error generating preview', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


