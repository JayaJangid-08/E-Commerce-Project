from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

ROLE_CHOICE = [
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
        ]

class Role(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    USERNAME_FIELD = 'username'
    email = models.EmailField(unique=True)
    roles = models.ManyToManyField(Role)

    REQUIRED_FIELDS = ['email']
    def __str__(self):
        return self.username

class Address(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    street = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    label = models.CharField(max_length=20 , choices=[('office' , 'Office'), ('home' , 'Home')])

    def __str__(self):
        return f"{self.user.username} - {self.city} ({self.label})"
    

