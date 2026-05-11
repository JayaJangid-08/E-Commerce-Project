from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Order
from .email import send_order_confirmation_email

@receiver(post_save, sender=Order)
def order_placedd(sender, instance, created, **kwargs):
    # Only when users are added
    if created and settings.SEND_EMAILS:
        try:
            print("EMAIL TRIGGERED")
            send_order_confirmation_email.delay(
                username= instance.customer.username,
                email= instance.customer.email,
                order_id= instance.id,
            )
        except Exception as e:
            print("EMAIL ERROR : ",e)



