from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'comment', 'rating', 'date', 'time']
        read_only_fields = ['id', 'user']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def get_date(self, obj):
        return obj.created_at.date()

    def get_time(self, obj):
        return obj.created_at.strftime("%I:%M %p")




