from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view , permission_classes
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Address , Role , User
from .serializers import RegistrationSerializer , AddressSerializer
from .permissions import IsCustomer , IsAdmin
# Create your views here.

@api_view(['GET', 'POST'])
def registration(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'GET':
        return Response({'message': 'Login View'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def switch_active_role(request):
    user = request.user
    user_roles = set(user.roles.values_list('name', flat=True))

    if request.method == 'GET':
        return Response({'active_role': user.active_role, 'all_roles': list(user_roles)})

    requested_role = request.data.get('role')
    if not requested_role:
        return Response({'error': 'role is required'}, status=status.HTTP_400_BAD_REQUEST)

    if requested_role not in user_roles:
        return Response({
            'error': f'You do not have the "{requested_role}" role',
            'your_roles': list(user_roles)}, status=status.HTTP_403_FORBIDDEN)

    user.active_role = requested_role
    user.save()

    return Response({
        'message': f'Switched to "{requested_role}" mode',
        'active_role': user.active_role,
        'all_roles': list(user_roles)
    })


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    user = request.user
    if request.method == 'GET':
        addresses = Address.objects.filter(user=user)
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': list(user.roles.values_list('name', flat=True)),
            'date_joined': user.date_joined.strftime("%Y-%m-%d"),
            'addresses': AddressSerializer(addresses, many=True).data
        })

    elif request.method == 'PUT':
        data = {}
        if 'username' in request.data:
            if User.objects.filter(username=request.data['username']).exclude(id=user.id).exists():
                return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
            data['username'] = request.data['username']

        if 'email' in request.data:
            if User.objects.filter(email=request.data['email']).exclude(id=user.id).exists():
                return Response({'error': 'Email already taken'}, status=status.HTTP_400_BAD_REQUEST)
            data['email'] = request.data['email']

        for key, value in data.items():
            setattr(user, key, value)
        user.save()

        return Response({
            'message': 'Profile updated successfully',
            'username': user.username,
            'email': user.email,
        })


CAN_ADD = {
    'customer': ['vendor'],       # customer can become vendor
    'vendor':   [],               # vendor can't add anything new
    'staff':    ['customer'],     # staff can add customer role
    'courier':  ['customer'],     # courier can add customer role
    'admin':    [],               # blocked entirely
}

# Customer role cannot be removed
CAN_REMOVE = {
    'customer': [],               # customer can't remove customer (base role)
    'vendor':   ['vendor'],       # vendor can drop vendor, revert to customer
    'staff':    ['customer'],     # staff can drop customer
    'courier':  ['customer'],     # courier can drop customer
    'admin':    [],               # blocked entirely
}

# Roles that can NEVER hold vendor, even if they also have customer
VENDOR_BLOCKED_ROLES = {'staff', 'courier', 'admin'}

def get_allowed_actions(user_roles: set) -> tuple[set, set]:
    can_add = set()
    can_remove = set()
    for role in user_roles:
        can_add.update(CAN_ADD.get(role, []))
        can_remove.update(CAN_REMOVE.get(role, []))

    # If user holds ANY privileged role, strip vendor from can_add entirely
    if user_roles & VENDOR_BLOCKED_ROLES:
        can_add.discard('vendor')

    return can_add, can_remove


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def remove_add_role(request):
    user = request.user
    user_roles = set(user.roles.values_list('name', flat=True))
    if request.method == 'GET':
        can_add, can_remove = get_allowed_actions(user_roles)
        return Response({
            'active_roles': list(user_roles),
            'can_add':      list(can_add - user_roles),     # Remove already-held roles
            'can_remove':   list(can_remove & user_roles),  # Only roles they actually have
        })
    action   = request.data.get('action')
    new_role = request.data.get('role')

    if action not in ['add', 'remove']:
        return Response({'error': 'action must be "add" or "remove"'}, status=status.HTTP_400_BAD_REQUEST)
    if not new_role:
        return Response({'error': '"role" field is required'}, status=status.HTTP_400_BAD_REQUEST)

    if 'admin' in user_roles:
        return Response({'error': 'Admins manage roles via the admin panel'}, status=status.HTTP_403_FORBIDDEN)
    can_add, can_remove = get_allowed_actions(user_roles)
    
    if action == 'add':
        if new_role not in can_add:
            return Response({
                    'error':   f'You cannot add the "{new_role}" role',
                    'can_add': list(can_add - user_roles),
                },
                status=status.HTTP_403_FORBIDDEN)
        if new_role in user_roles:
            return Response({'error': f'You already have the "{new_role}" role'}, status=status.HTTP_400_BAD_REQUEST)
        role_obj, _ = Role.objects.get_or_create(name=new_role)
        user.roles.add(role_obj)

    elif action == 'remove':
        if new_role not in can_remove:
            return Response({
                    'error':      f'You cannot remove the "{new_role}" role',
                    'can_remove': list(can_remove & user_roles),
                }, status=status.HTTP_403_FORBIDDEN)
        if new_role not in user_roles:
            return Response({'error': f'You do not have the "{new_role}" role'}, status=status.HTTP_400_BAD_REQUEST)
        
        role_obj = Role.objects.get(name=new_role)
        user.roles.remove(role_obj)
    updated_roles = set(user.roles.values_list('name', flat=True))
    can_add, can_remove = get_allowed_actions(updated_roles)

    return Response({
        'message':      f'Role "{new_role}" {action}ed successfully',
        'active_roles': list(updated_roles),
        'can_add':      list(can_add - updated_roles),
        'can_remove':   list(can_remove & updated_roles),
    }, status=status.HTTP_200_OK)


# views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def assign_role(request):
    user_id = request.data.get('user_id')
    role_name = request.data.get('role')

    ADMIN_ASSIGNABLE_ROLES = ['staff', 'courier', 'vendor']

    # Only superuser can assign admin
    if role_name == 'admin':
        if not request.user.is_superuser:
            return Response({'error': 'Only superuser can assign admin role'}, status=status.HTTP_403_FORBIDDEN)

    elif role_name not in ADMIN_ASSIGNABLE_ROLES:
        return Response({'error': f'Invalid role. Assignable roles: {ADMIN_ASSIGNABLE_ROLES}'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    role_obj, _ = Role.objects.get_or_create(name=role_name)
    user.roles.add(role_obj)
    return Response({
        'message': f'Role "{role_name}" assigned to {user.username}',
        'active_roles': list(user.roles.values_list('name', flat=True))
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['GET' , 'POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def address_list(request):
    if request.method == 'GET':
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET' , 'PUT' , 'DELETE'])
@permission_classes([IsAuthenticated, IsCustomer])
def address_detail(request, address_id):
    try:
        address = Address.objects.get(id = address_id)
    except Address.DoesNotExist:
        return Response({'message' : 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if address.user != request.user:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = AddressSerializer(address)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AddressSerializer(address, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        address.delete()
        return Response({'message' : 'Address deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

