from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .email import send_order_confirmation_email

@receiver(post_save, sender=Order)
def order_placedd(sender, instance, created, **kwargs):
    # Only when users are added
    if created:
            print("EMAIL TRIGGERED")
            send_order_confirmation_email.delay(
                username= instance.customer.username,
                email= instance.customer.email,
                order_id= instance.id,
            )

