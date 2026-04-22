from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import ProductSerializer , CategorySerializer
from .models import Product , Category
from Authenticate.permissions import IsAdmin , IsVendor , IsCustomer , IsVendorOrAdmin

# Create your views here.

@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products , many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not IsVendorOrAdmin().has_permission(request, None):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(vendor = request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET' , 'PUT' , 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not IsVendorOrAdmin().has_object_permission(request, None, product):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not IsVendorOrAdmin().has_object_permission(request, None, product):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({'message': 'Product deleted successfully'})
