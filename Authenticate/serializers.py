from .models import User , Address
from rest_framework import serializers

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(
        choices=['vendor', 'customer'],
        required=False
    )

    class Meta:
        model = User
        fields = ['username' , 'email' , 'password' , 'role']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    
    def validate_role(self, value):
        # Extra safety layer
        if value not in ['vendor', 'customer']:
            raise serializers.ValidationError("Invalid role")
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', 'customer')  # remove from dict safely

        user = User.objects.create_user(**validated_data)
        user.role = role
        user.save()

        return user

class AddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta : 
        model = Address
        fields = ['id', 'street', 'city', 'state', 'pincode', 'phone', 'label']
    
    def validate_pincode(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Enter valid pincode")
        return value
    
    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Enter valid Phone number")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Only 10 - 15 numbers are allowed")
        return value

    def validate(self, data):
        user = self.context['request'].user
        if Address.objects.filter(user=user).count() >= 5:
            raise serializers.ValidationError("Maximum 5 addresses are allowed")
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        return Address.objects.create(user=user, **validated_data)

