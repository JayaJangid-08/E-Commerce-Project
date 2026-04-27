from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .serializers import ProductSerializer , CategorySerializer
from .models import Product , Category
from Authenticate.permissions import IsAdmin , IsVendorOrAdmin

# Create your views here.

@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginator_products = paginator.paginate_queryset(products , request)
        serializer = ProductSerializer(paginator_products , many=True)
        return paginator.get_paginated_response(serializer.data)
    
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
        product = Product.objects.get(id = product_id)
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

@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated])
def category_list(request):
    if request.method == 'GET':
        category = Category.objects.all()
        serializer = CategorySerializer(category , many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not IsAdmin().has_permission(request , None):
            return Response({'message' : 'Permission denied'} , status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET' , 'PUT' , 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, category_id):
    try:
        category = Category.objects.get(id = category_id)
    except Category.DoesNotExist:
        return Response({'message' : 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not IsAdmin().has_permission(request , None):
            return Response({'message' : 'Premission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not IsAdmin().has_permission(request , None):
            return Response({'message' : 'Premission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        category.delete()
        return Response({'message' : 'Category deleted successfully'})

