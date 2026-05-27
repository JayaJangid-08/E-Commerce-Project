from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Authenticate.permissions import IsCustomer , IsAdmin
from Authenticate.models import User
from .models import Cart
from .serializers import CartSerializer

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def customer_cart(request, user_id):
    try:
        customer = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    cart_items = Cart.objects.filter(user=customer).select_related('product')
    serializer = CartSerializer(cart_items, many=True)
    return Response({
        'customer': customer.username,
        'total_items': cart_items.count(),
        'cart_items': serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def cart_list(request):
    if request.method == 'GET': 
        cart = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def add_product(request):
    if request.method == 'POST': 
        product_id = request.data.get('product')
        
        if Cart.objects.filter(user=request.user, product_id=product_id).exists():
            return Response({'message': 'Product already in cart'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CartSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET' , 'PUT'])
@permission_classes([IsAuthenticated, IsCustomer])
def cart_detail(request, item_id):
    try: 
        cart = Cart.objects.get(user=request.user, id=item_id)
    except Cart.DoesNotExist:
        return Response({'message' : 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = CartSerializer(cart, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsCustomer])
def remove_product(request, item_id):
    try: 
        cart = Cart.objects.get(user=request.user, id=item_id)
    except Cart.DoesNotExist:
        return Response({'message' : 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    cart.delete()
    return Response({'message' : 'Item removed successfully'}, status=status.HTTP_204_NO_CONTENT)


