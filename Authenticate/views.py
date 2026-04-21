from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RegistrationSerializer



from .models import User
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

