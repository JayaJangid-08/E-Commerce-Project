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

