from django.db import models
from django.utils import timezone
from Order.models import OrderItem , StatusChoice
from Authenticate.models import User


class VehicleType(models.TextChoices):
    BIKE = 'bike', 'Bike'
    SCOOTER = 'scooter', 'Scooter'
    CAR = 'car', 'Car'
    AUTO = 'auto', 'Auto'

class CourierProfile(models.Model):
    delivery_person = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_no = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices)
    vehicle_no = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.delivery_person.username


class DeliveryStatus(models.TextChoices):
    ASSIGNED = 'assigned', 'Assigned'
    PENDING_PICKUP = 'pending pickup', 'Pending Pickup'
    PICKED_UP = 'picked up', 'Picked Up'
    ON_THE_WAY = 'on the way', 'On The Way'
    ARRIVED_FOR_DELIVERY = 'arrived for delivery', 'Arrived For Delivery'
    DELIVERED = 'delivered', 'Delivered'

class DeliveryAssignment(models.Model):
    courier = models.ForeignKey(CourierProfile, on_delete=models.CASCADE, related_name='assignments')
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='delivery_assignment')
    delivery_status = models.CharField(max_length=30, choices=DeliveryStatus.choices, default=DeliveryStatus.ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.delivery_status == DeliveryStatus.DELIVERED and not self.delivered_at:
            self.delivered_at = timezone.now()
        super().save(*args, **kwargs)

        status_map = {
            DeliveryStatus.PICKED_UP: StatusChoice.SHIPPED,
            DeliveryStatus.ON_THE_WAY: StatusChoice.SHIPPED,
            DeliveryStatus.ARRIVED_FOR_DELIVERY: StatusChoice.SHIPPED,
            DeliveryStatus.DELIVERED: StatusChoice.DELIVERED,
        }

        if self.delivery_status in status_map:
            self.order_item.status = status_map[self.delivery_status]
            self.order_item.save()
            order = self.order_item.order

            if self.delivery_status == DeliveryStatus.DELIVERED:
                non_cancelled = order.order_items.exclude(status=StatusChoice.CANCELLED)
                if non_cancelled.exists() and not non_cancelled.exclude(status=StatusChoice.DELIVERED).exists():
                    order.status = StatusChoice.DELIVERED
                    order.save()
                    self._collect_cod_payment(order)
                elif order.status != StatusChoice.DELIVERED:
                    order.status = StatusChoice.SHIPPED
                    order.save()
    
    def _collect_cod_payment(self, order):
        try:
            from Payments.models import Payment, PaymentStatus, PaymentMethod
            payment = order.payment
            if payment.method == PaymentMethod.COD and payment.status == PaymentStatus.PENDING:
                payment.status = PaymentStatus.COLLECTED
                payment.paid_at = timezone.now()
                payment.save()
        except Payment.DoesNotExist:
            pass

    def __str__(self):
        return f"{self.order_item.id} - {self.courier.delivery_person.username}"

