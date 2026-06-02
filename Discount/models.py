from django.db import models
from django.utils.timezone import now
from Authenticate.models import User
from Products.models import Product
from django.core.exceptions import ValidationError

# Create your models here.

DISCOUNT_TYPE = [
    ('fixed', 'Fixed'),
    ('percentage', 'Percentage'),
]

class ApplicableTo(models.TextChoices):
    ALL = 'all', 'All Products'
    VENDOR = 'vendor', 'Vendor'
    PRODUCT = 'product', 'Single Product'

class Discount(models.Model):
    # who created it (admin/vendor)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_coupons") 
    coupon_name = models.CharField(max_length=50, unique=True)
    applicable_to = models.CharField(max_length=20, choices=ApplicableTo.choices)
    
    # only used if applicable_to == 'vendor'
    vendor = models.ForeignKey(
        User, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='vendor_coupons')
    
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='product_coupons')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    maximum_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.applicable_to == 'vendor' and not self.vendor:
            raise ValidationError("Vendor is required for vendor coupon")

        if self.applicable_to == 'product' and not self.product:
            raise ValidationError("Product is required for product-level coupon")

    class Meta:
            ordering = ['-created_at']

    def __str__(self):
        return f"{self.coupon_name} ({self.get_applicable_to_display()})"

    def is_expired(self):
        """Check if coupon is expired"""
        return self.expiry_date < now()

    def is_exhausted(self):
        """Check if usage limit reached"""
        return self.used_count >= self.usage_limit

    def is_valid(self):
        """Check if coupon is valid and can be used"""
        return self.is_active and not self.is_expired() and not self.is_exhausted()

    def clean(self):
        """Validate coupon based on applicable_to"""
        if self.applicable_to == 'vendor' and not self.vendor:
            raise ValidationError("Vendor is required for vendor coupon")

        if self.applicable_to == 'product' and not self.product:
            raise ValidationError("Product is required for product-level coupon")

        # Validate discount amount
        if self.discount_type == 'percentage' and self.discount_amount > 100:
            raise ValidationError("Percentage discount cannot exceed 100%")



