from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import CourierProfile , DeliveryAssignment , DeliveryStatus
from .serializers import CourierProfileSerializer , DeliveryAssignmentSerializer
from Authenticate.permissions import IsCourier , IsAdmin

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCourier])
def create_courier_profile(request):
    if CourierProfile.objects.filter(delivery_person=request.user).exists():
        return Response({'message': 'Courier profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = CourierProfileSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(delivery_person=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsCourier])
def courier_profile(request):
    try:
        courier = CourierProfile.objects.get(delivery_person=request.user)
    except CourierProfile.DoesNotExist:
        return Response({'message': 'Courier profile not found'},status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CourierProfileSerializer(courier)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = CourierProfileSerializer(courier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        courier.is_available = False
        courier.save()
        return Response({'message': 'Courier profile deactivated successfully'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdmin])
def verify_courier(request, courier_id):
    try:
        courier = CourierProfile.objects.get(id=courier_id)
    except CourierProfile.DoesNotExist:
        return Response({'message': 'Courier not found'}, status=status.HTTP_404_NOT_FOUND)

    courier.is_verified = True
    courier.save()

    return Response({
        'message': f'Courier {courier.delivery_person.username} verified successfully',
        'is_verified': courier.is_verified
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def assign_delivery(request):
    courier_id = request.data.get('courier')
    try:
        courier = CourierProfile.objects.get(id=courier_id)
        if not courier.is_verified:
            return Response({'message': 'Courier is not verified yet'}, status=status.HTTP_400_BAD_REQUEST)
    except CourierProfile.DoesNotExist:
        return Response({'message': 'Courier not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DeliveryAssignmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCourier])
def assigned_deliveries(request):
    assignments = DeliveryAssignment.objects.filter(courier__delivery_person=request.user)
    serializer = DeliveryAssignmentSerializer(assignments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def courier_list(request):
    if IsAdmin().has_permission(request, None):
        couriers = CourierProfile.objects.filter(is_available=True)
    elif IsCourier().has_permission(request, None):
        couriers = CourierProfile.objects.filter(delivery_person=request.user)
    else:
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    serializer = CourierProfileSerializer(couriers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def courier_detail(request, courier_id):
    try:
        courier = CourierProfile.objects.get(id=courier_id)
    except CourierProfile.DoesNotExist:
        return Response({'message': 'Courier not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if IsCourier().has_permission(request, None):
        if not courier.assignments.filter(courier__delivery_person=request.user).exists():
            return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    elif not IsAdmin().has_permission(request, None):
        return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CourierProfileSerializer(courier)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCourier])
def assignment_detail(request, assignment_id):
    try:
        assignment = DeliveryAssignment.objects.get(id=assignment_id, courier__delivery_person=request.user)
    except DeliveryAssignment.DoesNotExist:
        return Response({'message': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DeliveryAssignmentSerializer(assignment)
    return Response(serializer.data)


VALID_TRANSITIONS = {
    DeliveryStatus.ASSIGNED: [DeliveryStatus.PENDING_PICKUP],
    DeliveryStatus.PENDING_PICKUP: [DeliveryStatus.PICKED_UP],
    DeliveryStatus.PICKED_UP: [DeliveryStatus.ON_THE_WAY],
    DeliveryStatus.ON_THE_WAY: [DeliveryStatus.ARRIVED_FOR_DELIVERY],
    DeliveryStatus.ARRIVED_FOR_DELIVERY: [DeliveryStatus.DELIVERED]
}


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsCourier])
def update_delivery_status(request, assignment_id):
    try:
        assignment = DeliveryAssignment.objects.get(id=assignment_id, courier__delivery_person=request.user)
    except DeliveryAssignment.DoesNotExist:
        return Response({'message': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if not new_status:
        return Response({'message': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    allowed_statuses = VALID_TRANSITIONS.get(assignment.delivery_status, [])
    if new_status not in allowed_statuses:
        return Response({'message': 'Invalid status transition'}, status=status.HTTP_400_BAD_REQUEST)

    assignment.delivery_status = new_status
    assignment.save()
    return Response({'message': 'Delivery status updated successfully', 'status': assignment.delivery_status})

