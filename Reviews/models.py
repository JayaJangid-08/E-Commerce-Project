from django.db import models
from Authenticate.models import User
from Products.models import Product

# Create your models here.
class Rating(models.IntegerChoices):
    ONE = 1, "1 Star"
    TWO = 2, "2 Stars"
    THREE = 3, "3 Stars"
    FOUR = 4, "4 Stars"
    FIVE = 5, "5 Stars"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    rating = models.IntegerField(choices=Rating.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_review'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


