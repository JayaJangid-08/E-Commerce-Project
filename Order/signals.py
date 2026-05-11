from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .email import send_order_confirmation_email

@receiver(post_save, sender=Order)
def order_placedd(sender, instance, created, **kwargs):
    if created:
        print("EMAIL TRIGGERED")
        try:
            send_order_confirmation_email(
                username=instance.customer.username,
                email=instance.customer.email,
                order_id=instance.id,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")


