from django.db import models
from Products.models import Product
from Authenticate.models import User

# Create your models here.

MOVEMENT_CHOICES = [
    ('purchase', 'Purchase'),
    ('sale', 'Sale'),
    ('return', 'Return'),
    ('damage', 'Damage'),
    ('manual_add', 'Manual Add'),      # Added for add_stock_in_warehouse
    ('manual_remove', 'Manual Remove'), # Added for remove_stock_from_warehouse
    ('order', 'Order'),                 # Added for order fulfillment
]


class Warehouse(models.Model):
    name = models.CharField(max_length=40)
    location = models.CharField(max_length=40)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Inventory(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventories')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields=['warehouse', 'product'],
            name='unique_warehouse_product'
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}"


class StockMovement(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_movement')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movement')
    quantity_change = models.IntegerField()  # +10 or -2
    reason = models.CharField(max_length=100, choices=MOVEMENT_CHOICES)  # order, manual, return
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.warehouse} - {self.product} - {self.reason}"


class StaffWarehouse(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields=['staff', 'warehouse'],
            name='unique_staff_warehouse'
            )
        ]
    
    def __str__(self):
        return f"{self.staff.username} - {self.warehouse.name}"

