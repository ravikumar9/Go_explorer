from django.contrib import admin
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


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "hotel", "discount_type", "discount_value", "is_active")
    list_filter = ("hotel", "is_active")
    search_fields = ("code",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
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
