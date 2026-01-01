from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date
from decimal import Decimal

from .models import Hotel, RoomType, RoomPlan, Booking, Coupon


def home(request):
    return render(request, "booking/home.html", {
        "today": date.today().isoformat()
    })


def hotels_list(request):
    hotels = Hotel.objects.filter(is_active=True)
    return render(request, "booking/hotel_list.html", {
        "hotels": hotels,
        "check_in": request.GET.get("check_in"),
        "check_out": request.GET.get("check_out"),
    })


def rooms_list(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    return render(request, "booking/room_list.html", {
        "hotel": hotel,
        "rooms": RoomType.objects.filter(hotel=hotel),
        "images": hotel.images.all(),
        "check_in": request.GET.get("check_in"),
        "check_out": request.GET.get("check_out"),
    })


def review_booking(request):
    plan = get_object_or_404(RoomPlan, id=request.GET["plan_id"])

    check_in = request.GET["check_in"]
    check_out = request.GET["check_out"]

    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

    nights = (check_out_date - check_in_date).days

    base_fare = Decimal(plan.price) * nights
    gst = (base_fare * Decimal("0.18")).quantize(Decimal("0.01"))
    total = base_fare + gst

    coupons = Coupon.objects.filter(
        hotel=plan.room_type.hotel,
        is_active=True
    )

    return render(request, "booking/review_booking.html", {
        "plan": plan,
        "hotel": plan.room_type.hotel,
        "check_in": check_in,
        "check_out": check_out,
        "nights": nights,
        "base_fare": base_fare,
        "gst": gst,
        "total": total,
        "coupons": coupons,
    })


def create_booking(request):
    if request.method != "POST":
        return redirect("home")

    plan = get_object_or_404(RoomPlan, id=request.POST["plan_id"])

    check_in = datetime.strptime(request.POST["check_in"], "%Y-%m-%d").date()
    check_out = datetime.strptime(request.POST["check_out"], "%Y-%m-%d").date()

    total = Decimal(request.POST["total"])
    coupon_code = request.POST.get("coupon_code")
    discount = Decimal("0")

    if coupon_code:
        try:
            coupon = Coupon.objects.get(
                code=coupon_code,
                hotel=plan.room_type.hotel,
                is_active=True
            )
            if coupon.discount_type == "PERCENT":
                discount = (total * coupon.discount_value / 100).quantize(Decimal("0.01"))
            else:
                discount = Decimal(coupon.discount_value)
        except Coupon.DoesNotExist:
            pass

    booking = Booking.objects.create(
        room_plan=plan,
        guest_name=request.POST["guest_name"],
        guest_email=request.POST["email"],
        guest_phone=request.POST["phone"],
        check_in=check_in,
        check_out=check_out,
        coupon_code=coupon_code,
        discount_amount=discount,
        amount=total - discount,
    )

    return redirect("payment_page", booking_id=booking.id)


def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "booking/payment.html", {"booking": booking})


def payment_success(request):
    return render(request, "booking/success.html")
