# booking/tasks.py
from datetime import timedelta
from django.utils.timezone import now
from django.db import transaction
from .models import Booking, Availability

@transaction.atomic
def auto_cancel_unpaid_bookings():
    expiry_time = now() - timedelta(minutes=10)

    bookings = Booking.objects.select_for_update().filter(
        status="PENDING_PAYMENT",
        created_at__lt=expiry_time
    )

    for booking in bookings:
        current = booking.check_in
        while current < booking.check_out:
            availability = Availability.objects.get(
                room_type=booking.room_type,
                date=current
            )
            availability.available_rooms += 1
            availability.save()
            current += timedelta(days=1)

        booking.status = "CANCELLED"
        booking.save()
