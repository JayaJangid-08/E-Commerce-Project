from django.db import models
from Products.models import Product
from Authenticate.models import User

# Create your models here.

STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
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
    delivery_address = models.OneToOneField(OrderAddress, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateField(auto_now_add=True)
    discounted_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    final_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')


    def __str__(self):
        return f"{self.order} - {self.product.name}"


