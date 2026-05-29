from django.db import models
from Products.models import Product
from Authenticate.models import User

# Create your models here.

class StatusChoice:
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'


STATUS_CHOICES = [
        (StatusChoice.CONFIRMED, 'Confirmed'),
        (StatusChoice.SHIPPED, 'Shipped'),
        (StatusChoice.DELIVERED, 'Delivered'),
        (StatusChoice.CANCELLED, 'Cancelled'),
]


class OrderAddress(models.Model):
    full_name = models.CharField(max_length=100)
    street = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(OrderAddress, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='confirmed')
    order_date = models.DateField(auto_now_add=True)
    discount_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    final_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = Order.objects.get(pk=self.pk).status
        super().save(*args, **kwargs)
        if old_status != self.status:
            self.order_items.update(status=self.status)

    def __str__(self):
        return f"{self.customer.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

    # SNAPSHOT FIELDS
    product_name = models.CharField(max_length=255)
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.URLField(blank=True, null=True)
    product_category = models.CharField(max_length=100, blank=True, null=True)
    vendor_name = models.CharField(max_length=100, blank=True, null=True)

    quantity = models.PositiveIntegerField(default=1)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='confirmed')
    
    def __str__(self):
        return f"{self.order.id} - {self.product_name}"




