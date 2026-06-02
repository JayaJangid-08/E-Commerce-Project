from rest_framework import serializers
from .models import Discount

class DiscountSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Discount
        fields = '__all__'


