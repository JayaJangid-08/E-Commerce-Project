from django.db.models.signals import post_save 
from django.dispatch import receiver
from .models import User, Role

# Authenticate/signals.py

@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:  # Applicabele on new user only but not on SUPERUSER
        customer_role, _ = Role.objects.get_or_create(name='customer')
        instance.roles.add(customer_role)
        User.objects.filter(pk=instance.pk).update(active_role='customer')


