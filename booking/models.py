from django.db import models
from django.core.exceptions import ValidationError


# -------------------------
# HOTEL
# -------------------------
class Hotel(models.Model):
    RATING_CHOICES = (
        (3, "3 Star"),
        (4, "4 Star"),
        (5, "5 Star"),
    )

    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def starting_price(self):
        """Return the minimum room plan price for this hotel (or 0)."""
        plans = RoomPlan.objects.filter(room_type__hotel=self).order_by("price")
        if plans.exists():
            return plans.first().price
        return 0


# -------------------------
# HOTEL IMAGES
# -------------------------
class HotelImage(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="hotels/")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.hotel.name} image"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # unset other primary images for this hotel
            type(self).objects.filter(hotel=self.hotel, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


# -------------------------
# AMENITY
# -------------------------
class Amenity(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# -------------------------
# ROOM TYPE
# -------------------------
class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # legacy `price` column exists in migrations/DB; keep a mapped field to remain compatible
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='price')

    base_price = models.PositiveIntegerField(default=0)
    room_size_sqft = models.PositiveIntegerField(default=0)
    total_rooms = models.PositiveIntegerField(default=0)

    amenities = models.ManyToManyField(Amenity, blank=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


# -------------------------
# ROOM PLAN
# -------------------------
class RoomPlan(models.Model):
    PLAN_CHOICES = (
        ("ROOM_ONLY", "Room Only"),
        ("BREAKFAST", "Room + Breakfast"),
        ("HALF_BOARD", "Room + Lunch/Dinner"),
        ("FULL_BOARD", "Room + All Meals"),
    )

    room_type = models.ForeignKey(
        RoomType,
        related_name="plans",
        on_delete=models.CASCADE
    )
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.room_type} - {self.get_plan_type_display()}"


# -------------------------
# COUPON (HOTEL SPECIFIC)
# -------------------------
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("PERCENT", "Percentage"),
        ("FLAT", "Flat Amount"),
    )

    code = models.CharField(max_length=20)
    hotel = models.ForeignKey(
        Hotel,
        related_name="coupons",
        on_delete=models.CASCADE
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.hotel.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["hotel", "code"], name="unique_coupon_per_hotel"),
        ]


# -------------------------
# BOOKING
# -------------------------
class Booking(models.Model):
    STATUS_CHOICES = (
        ("PENDING_PAYMENT", "Pending Payment"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    )

    room_plan = models.ForeignKey(RoomPlan, on_delete=models.CASCADE)

    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=15)

    check_in = models.DateField()
    check_out = models.DateField()

    coupon_code = models.CharField(max_length=20, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING_PAYMENT"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest_name} - {self.room_plan}"

    def clean(self):
        # Ensure dates are valid
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValidationError("`check_out` must be after `check_in`")
