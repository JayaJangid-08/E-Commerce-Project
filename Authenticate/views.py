from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from .serializers import RegistrationSerializer , AddressSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import User , Address
from .permissions import IsCustomer
# Create your views here.

@api_view(['GET', 'POST'])
def registration(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully'})
        return Response(serializer.errors)
    elif request.method == 'GET':
        return Response({'message': 'Signup View'})

@api_view(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=400)
    elif request.method == 'GET':
        return Response({'message': 'Login View'})

@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated])
def address_list(request):
    if request.method == 'GET':
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not IsCustomer().has_permission(request, None):
            return Response({'message' : 'Only customer can create address'}, status=403)
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

@api_view(['GET' , 'PUT' , 'DELETE'])
@permission_classes([IsAuthenticated])
def address_detail(request, address_id):
    try:
        address = Address.objects.get(user = request.user, id = address_id)
    except Address.DoesNotExist:
        return Response({'message' : 'Address not found'}, status=404)
    
    if request.method == 'GET':
        serializer = AddressSerializer(address)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if not IsCustomer().has_permission(request , None):
            return Response({'message' : 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AddressSerializer(address, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not IsCustomer().has_permission(request, None):
            return Response({'message' : 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        address.delete()
        return Response({'message' : 'Address deleted successfully'})

