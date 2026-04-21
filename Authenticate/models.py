from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    USERNAME_FIELD = 'username'
    email = models.EmailField(unique=True)
    ROLE_CHOICE = [
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
        ]
    role = models.CharField(max_length=20 , choices= ROLE_CHOICE)

    REQUIRED_FIELDS = ['email', 'role']
    def __str__(self):
        return self.username

