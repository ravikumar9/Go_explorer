from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date
from decimal import Decimal

from .models import Hotel, RoomType, RoomPlan, Booking, Coupon
from django.http import JsonResponse


def home(request):
    return render(request, "booking/home.html", {
        "today": date.today().isoformat(),
        "city": request.GET.get("city", ""),
        "check_in": request.GET.get("check_in", ""),
        "check_out": request.GET.get("check_out", ""),
    })


def hotels_list(request):
    qs = Hotel.objects.filter(is_active=True)

    # Filters
    selected_city = request.GET.get("city", "")
    selected_rating = request.GET.get("rating", "")
    selected_price = request.GET.get("price", "")
    selected_sort = request.GET.get("sort", "relevance")

    if selected_city:
        qs = qs.filter(city__icontains=selected_city)
    if selected_rating:
        try:
            qs = qs.filter(rating=int(selected_rating))
        except ValueError:
            pass

    hotels = list(qs)

    # Sorting
    if selected_sort == "price_low":
        hotels.sort(key=lambda h: float(h.starting_price or 0))
    elif selected_sort == "price_high":
        hotels.sort(key=lambda h: float(h.starting_price or 0), reverse=True)
    elif selected_sort == "rating":
        hotels.sort(key=lambda h: h.rating, reverse=True)

    return render(request, "booking/hotel_list.html", {
        "hotels": hotels,
        "check_in": request.GET.get("check_in"),
        "check_out": request.GET.get("check_out"),
        "selected_city": selected_city,
        "selected_rating": selected_rating,
        "selected_price": selected_price,
        "selected_sort": selected_sort,
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


def validate_coupon(request):
    code = request.GET.get("code")
    plan_id = request.GET.get("plan_id")
    total = request.GET.get("total")
    try:
        total = Decimal(total)
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid_total"}, status=400)

    try:
        plan = RoomPlan.objects.get(id=plan_id)
    except RoomPlan.DoesNotExist:
        return JsonResponse({"ok": False, "error": "invalid_plan"}, status=400)

    if not code:
        return JsonResponse({"ok": False, "error": "no_code"}, status=400)

    try:
        coupon = Coupon.objects.get(code=code, hotel=plan.room_type.hotel, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)

    if coupon.discount_type == "PERCENT":
        discount = (total * coupon.discount_value / 100).quantize(Decimal("0.01"))
    else:
        discount = Decimal(coupon.discount_value)

    payable = (total - discount).quantize(Decimal("0.01"))

    return JsonResponse({
        "ok": True,
        "code": coupon.code,
        "discount": str(discount),
        "payable": str(payable),
    })


def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, "booking/payment.html", {"booking": booking})


def payment_success(request):
    return render(request, "booking/success.html")
