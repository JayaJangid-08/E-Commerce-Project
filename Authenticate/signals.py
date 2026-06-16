# Authenticate/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Role

@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    if created:  # Applicabele on new user only
        customer_role, _ = Role.objects.get_or_create(name='customer')
        instance.roles.add(customer_role)

