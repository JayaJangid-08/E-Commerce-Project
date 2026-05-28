from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.db.models import Avg

from .models import Review
from Products.models import Product
from Order.models import OrderItem
from Authenticate.permissions import IsCustomer, IsReviewOwnerOrAdmin
from .serializers import ReviewSerializer

# Create your views here.

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def review_list(request, product_id):
    try:
        product = Product.objects.get(id = product_id)
    except Product.DoesNotExist:
        return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        reviews = product.reviews.all()
        paginator = PageNumberPagination()
        paginator.page_size = 5
        paginator_review = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(paginator_review, many=True)
        average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        response_data = {
            'reviews': serializer.data,
            'average_rating': round(average_rating, 1) if average_rating else 0,
            'total_reviews': reviews.count()
        }
        return paginator.get_paginated_response(response_data)

    elif request.method == 'POST':
        if not IsCustomer().has_permission(request , None):
            return Response({'message' : 'Only Customer can review products'}, status=status.HTTP_403_FORBIDDEN)
        
        has_delivered_order = OrderItem.objects.filter(
            order__customer=request.user,
            product=product,
            status='delivered'
            ).exists()
        
        if not has_delivered_order:
            return Response({'message' : 'Only delivered products can be reviewed'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Review.objects.filter(user=request.user, product=product).exists():
            return Response({'message': 'Review already exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def review_detail(request, review_id):
    try:
        review = Review.objects.get(id = review_id)
    except Review.DoesNotExist:
        return Response({'message': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    if not IsReviewOwnerOrAdmin().has_object_permission(request, None, review):
            return Response({'message' : 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        review.delete()
        return Response({'message' : 'Review removed successfully'}, status=status.HTTP_200_OK)

