from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache

from .serializers import ProductSerializer , CategorySerializer
from .models import Product , Category
from Authenticate.permissions import IsAdmin , IsVendorOrAdmin

# Create your views here.

def bump_product_version():
    if cache.get("product-version") is None:
        cache.set("product-version", 1)
    else:
        cache.incr("product-version")

@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated])
def product_list(request):
    if request.method == 'GET':
        version = cache.get("product-version") or 1
        cache.set("product-version", version)
        params = request.GET.urlencode()
        cache_key = f"products:v{version}:{params}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)
        products = Product.objects.all()
        # Filtering
        category = request.query_params.get('category')
        vendor = request.query_params.get('vendor')
        search = request.query_params.get('search')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        ordering = request.query_params.get('ordering', 'created_at')
        if category:
            products = products.filter(category__name__iexact=category)
        if vendor:
            products = products.filter(vendor=vendor)
        if search:
            products = products.filter(name__icontains=search)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        allowed_ordering = ['price', 'created_at', '-price', '-created_at']
        ordering = request.query_params.get('ordering', 'created_at')
        if ordering not in allowed_ordering:
            ordering = 'created_at'

        products = products.order_by(ordering)
        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginator_products = paginator.paginate_queryset(products , request)
        serializer = ProductSerializer(paginator_products , many=True)
        response = paginator.get_paginated_response(serializer.data)
        cache.set(cache_key, response.data, timeout=60*5)  # Stores for 5 mins
        return response

    elif request.method == 'POST':
        if not IsVendorOrAdmin().has_permission(request, None):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(vendor = request.user)
            bump_product_version()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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
            bump_product_version()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not IsVendorOrAdmin().has_object_permission(request, None, product):
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        product.delete()
        bump_product_version()
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            return Response({'message' : 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if not IsAdmin().has_permission(request , None):
            return Response({'message' : 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        category.delete()
        return Response({'message' : 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

