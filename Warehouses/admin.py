from django.contrib import admin
from .models import Warehouse , Inventory , StaffWarehouse , StockMovement

# Register your models here.
admin.site.register(Warehouse)
admin.site.register(Inventory)
admin.site.register(StockMovement)
admin.site.register(StaffWarehouse)
