from django.contrib import admin
from .models import Hotel, RoomType, Booking, Availability


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "is_active")
    search_fields = ("name", "city")


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "hotel", "price", "total_rooms")
    list_filter = ("hotel",)


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("room_type", "date", "available_rooms")
    list_filter = ("date",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "guest_name", "room_type", "check_in", "check_out", "status")
    list_filter = ("status",)
