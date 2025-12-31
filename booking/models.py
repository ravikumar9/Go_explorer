from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.IntegerField()

    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class Availability(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    date = models.DateField()
    available_rooms = models.IntegerField()

    class Meta:
        unique_together = ("room_type", "date")

    def __str__(self):
        return f"{self.room_type} | {self.date}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ("PENDING_PAYMENT", "Pending Payment"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("FAILED", "Failed"),
    )

    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guest_name = models.CharField(max_length=100)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # ✅ FIX HERE
    guest_email = models.EmailField(null=True, blank=True)
    guest_phone = models.CharField(max_length=15, blank=True, null=True)
    payment_method = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING_PAYMENT"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    booking = models.OneToOneField(
        "Booking",
        on_delete=models.CASCADE,
        related_name="payment"
    )
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    idempotency_key = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20)  # INITIATED, SUCCESS, FAILED
    created_at = models.DateTimeField(auto_now_add=True)

