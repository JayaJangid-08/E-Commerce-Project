from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    USERNAME_FIELD = 'username'
    ROLE_CHOICE = [
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
        ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20 , choices= ROLE_CHOICE , default='customer')

    REQUIRED_FIELDS = ['email']
    def __str__(self):
        return self.username

class Address(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE )
    street = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    phone = models.CharField(max_length=15)
    label = models.CharField(max_length=20 , choices=[('office' , 'Office'), ('house' , 'House')])

    def __str__(self):
        return f"{self.user.username} - {self.city} ({self.label})"
    

