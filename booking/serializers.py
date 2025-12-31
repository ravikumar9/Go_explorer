from rest_framework import serializers
from .models import Booking, RoomType


class BookingCreateSerializer(serializers.Serializer):
    room_type_id = serializers.IntegerField()
    guest_name = serializers.CharField(max_length=100)
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate(self, data):
        if data["check_in"] >= data["check_out"]:
            raise serializers.ValidationError("Invalid date range")
        return data
