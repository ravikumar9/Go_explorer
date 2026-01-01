from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Hotel, HotelImage, RoomType, RoomPlan,
    Amenity, Booking, Coupon
)


class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "rating", "is_active")
    list_filter = ("city", "rating", "is_active")
    search_fields = ("name", "city")
    inlines = [HotelImageInline]


class RoomPlanInline(admin.TabularInline):
    model = RoomPlan
    extra = 1


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hotel",
        "base_price",
        "room_size_sqft",
        "total_rooms",
    )
    inlines = [RoomPlanInline]


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        hotel = cleaned.get("hotel")
        code = cleaned.get("code")
        if hotel and code:
            qs = Coupon.objects.filter(hotel=hotel, code=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("A coupon with this code already exists for the selected hotel.")
        return cleaned


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    form = CouponForm
    list_display = ("code", "hotel", "discount_type", "discount_value", "is_active")
    list_filter = ("hotel", "is_active")
    search_fields = ("code",)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        if check_in and check_out and check_in >= check_out:
            raise ValidationError("`check_out` must be after `check_in`")
        return cleaned


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingForm
    list_display = (
        "guest_name",
        "room_plan",
        "check_in",
        "check_out",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("guest_name", "guest_email", "guest_phone")


admin.site.register(Amenity)
