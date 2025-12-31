from django.shortcuts import render, redirect, get_object_or_404
from .models import Hotel, RoomType, Booking
from datetime import datetime

def home(request):
    return render(request, "booking/home.html")

def hotels_list(request):
    city = request.GET.get("city")
    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")

    hotels = Hotel.objects.all()
    if city:
        hotels = hotels.filter(city__icontains=city)

    context = {
        "hotels": hotels,
        "check_in": check_in,
        "check_out": check_out,
    }
    return render(request, "booking/hotel_list.html", context)

def rooms_list(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = RoomType.objects.filter(hotel=hotel)

    context = {
        "hotel": hotel,
        "rooms": rooms,
        "check_in": request.GET.get("check_in"),
        "check_out": request.GET.get("check_out"),
    }
    return render(request, "booking/room_list.html", context)

def review_booking(request):
    room_id = request.GET.get("room_type_id")
    room = get_object_or_404(RoomType, id=room_id)

    check_in = datetime.strptime(request.GET.get("check_in"), "%Y-%m-%d")
    check_out = datetime.strptime(request.GET.get("check_out"), "%Y-%m-%d")
    nights = (check_out - check_in).days

    base_fare = room.price * nights
    gst = round(base_fare * 0.18, 2)
    total = base_fare + gst

    context = {
        "room": room,
        "hotel": room.hotel,
        "check_in": check_in.date(),
        "check_out": check_out.date(),
        "base_fare": base_fare,
        "gst": gst,
        "total": total,
    }
    return render(request, "booking/review_booking.html", context)

def create_booking(request):
    if request.method == "POST":
        booking = Booking.objects.create(
            guest_name=request.POST.get("first_name") + " " + request.POST.get("last_name"),
            guest_email=request.POST.get("email"),
            guest_phone=request.POST.get("phone"),
            room_type_id=request.POST.get("room_id"),
            check_in=request.POST.get("check_in"),
            check_out=request.POST.get("check_out"),
            total_amount=request.POST.get("total"),
        )
        return redirect("payment_page", booking_id=booking.id)

    return redirect("home")

def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "booking/payment.html", {"booking": booking})

def payment_success(request):
    return render(request, "booking/success.html")
