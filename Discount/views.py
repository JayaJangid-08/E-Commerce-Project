from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Authenticate.permissions import IsDiscountOwnerOrAdmin
from .serializers import DiscountSerializer
from .models import Discount

# Create your views here.

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def discount_list(request):
    if request.method == 'GET':
        discount = Discount.objects.all()
        serializer = DiscountSerializer(discount, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not IsDiscountOwnerOrAdmin().has_permission(request, None):
            return Response({'message' : 'Permision denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = DiscountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def discount_detail(request, coupon_id):
    try:
        discount = Discount.objects.get(id = coupon_id)
    except Discount.DoesNotExist:
        return Response({'message' : 'Coupon not Found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = DiscountSerializer(discount)
        return Response(serializer.data)
    
    permission = IsDiscountOwnerOrAdmin()
    if not permission.has_object_permission(request, None, discount):
        return Response({'message' : 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':        
        serializer = DiscountSerializer(discount, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        discount.delete()
        return Response({'message' : 'Coupon deleted successfully'})

