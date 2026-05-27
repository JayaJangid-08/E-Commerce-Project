from django.db import models
from Products.models import Product
from Authenticate.models import User

# Create your models here.
 
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate items
        ordering = ['-created_at']              # Newest first

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x {self.quantity}"
    
    def get_item_total(self):
        """Calculate total price for this cart item"""
        return self.product.price * self.quantity