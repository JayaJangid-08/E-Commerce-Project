from django.conf import settings
from django.core.mail import EmailMessage
from celery import shared_task


@shared_task
def send_order_confirmation_email(username, email, order_id):
    subject = "Order Placed Successfully"
    message = f"Hi {username}, Your order {order_id} have been placed successfully."
    email_message = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
            )
    
    try:
        email_message.send(fail_silently=False)
        print("EMAIL SENT to", email)
        return True
    
    except Exception as e:
        print("EMAIL FAILED", e)
        return False

