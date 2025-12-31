from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from .notifications import (
    send_booking_confirmation,
    send_booking_cancellation,
    send_payment_failed
)

@receiver(post_save, sender=Booking)
def booking_status_handler(sender, instance, created, **kwargs):

    if created:
        return

    if instance.status == "CONFIRMED":
        send_booking_confirmation(instance)

    elif instance.status == "CANCELLED":
        send_booking_cancellation(instance)

    elif instance.status == "PAYMENT_FAILED":
        send_payment_failed(instance)

    elif instance.status == "REFUNDED":
        send_refund_confirmation(instance)

