from django.contrib import admin
from .models import DeliveryAssignment , CourierProfile

# Register your models here.

admin.site.register(CourierProfile)
admin.site.register(DeliveryAssignment)
