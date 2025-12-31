from django.shortcuts import render, redirect, get_object_or_404
from .models import Hotel, RoomType, Booking
from datetime import datetime, date
from decimal import Decimal
from django.conf import settings

# -------------------------
# HOME
# -------------------------
def home(request):
    today = date.today().isoformat()
    return render(request, "booking/home.html", {
        "today": today
    })


# -------------------------
# HOTEL LIST
# -------------------------
def hotels_list(request):
    city = request.GET.get("city")
    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")

    hotels = Hotel.objects.all()
    if city:
        hotels = hotels.filter(city__icontains=city)

    return render(request, "booking/hotel_list.html", {
        "hotels": hotels,
        "check_in": check_in,
        "check_out": check_out,
    })


# -------------------------
# ROOMS LIST
# -------------------------
def rooms_list(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = RoomType.objects.filter(hotel=hotel)

    return render(request, "booking/room_list.html", {
        "hotel": hotel,
        "rooms": rooms,
        "check_in": request.GET.get("check_in"),
        "check_out": request.GET.get("check_out"),
    })


# -------------------------
# REVIEW BOOKING (SAFE FIX)
# -------------------------
def review_booking(request):
    room_id = request.GET.get("room_type_id")
    check_in_raw = request.GET.get("check_in")
    check_out_raw = request.GET.get("check_out")

    if not (room_id and check_in_raw and check_out_raw):
        return redirect("home")

    room = get_object_or_404(RoomType, id=room_id)

    # SAFE date parsing
    check_in = datetime.strptime(check_in_raw, "%Y-%m-%d").date()
    check_out = datetime.strptime(check_out_raw, "%Y-%m-%d").date()

    nights = (check_out - check_in).days
    nights = max(nights, 1)

    base_fare = Decimal(room.price) * nights
    gst = (base_fare * Decimal("0.18")).quantize(Decimal("0.01"))
    total = base_fare + gst

    return render(request, "booking/review_booking.html", {
        "room": room,
        "hotel": room.hotel,
        "check_in": check_in,
        "check_out": check_out,
        "base_fare": base_fare,
        "gst": gst,
        "total": total,
        "nights": nights,
    })


# -------------------------
# CREATE BOOKING (NO CRASH)
# -------------------------
def create_booking(request):
    if request.method != "POST":
        return redirect("home")

    # ---- SAFE DATE PARSING ----
    check_in_raw = request.POST.get("check_in")
    check_out_raw = request.POST.get("check_out")

    try:
        check_in = datetime.strptime(check_in_raw, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_raw, "%Y-%m-%d").date()
    except ValueError:
        check_in = datetime.strptime(check_in_raw, "%b. %d, %Y").date()
        check_out = datetime.strptime(check_out_raw, "%b. %d, %Y").date()

    booking = Booking.objects.create(
        guest_name=f"{request.POST.get('first_name')} {request.POST.get('last_name')}",
        guest_email=request.POST.get("email"),
        guest_phone=request.POST.get("phone"),
        room_type_id=request.POST.get("room_type_id"),

        check_in=check_in,
        check_out=check_out,

        amount=Decimal(request.POST.get("total")),

        # ✅ THIS IS THE CRITICAL FIX
        status="PENDING_PAYMENT"
    )

    return redirect("payment_page", booking_id=booking.id)


# -------------------------
# PAYMENT
# -------------------------
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # 🚫 BLOCK invalid states
    if booking.status != "PENDING_PAYMENT":
        return redirect("home")   # or booking details page

    return render(request, "booking/payment.html", {
        "booking": booking,
        "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID
    })


def payment_success(request):
    return render(request, "booking/success.html")
