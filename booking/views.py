import json
import razorpay
import hmac
import hashlib

from datetime import datetime, timedelta
from rest_framework.permissions import AllowAny

from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Hotel, RoomType, Booking, Availability, Payment
from .serializers import BookingCreateSerializer
from .razorpay_client import client
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt



# =====================================================
# API ROOT
# =====================================================
def api_root(request):
    return JsonResponse({
        "message": "GoExplorer Booking API is running 🚀"
    })


# =====================================================
# HOTEL APIs
# =====================================================
def hotel_list(request):
    hotels = list(Hotel.objects.values())
    return JsonResponse(hotels, safe=False)


def hotel_detail(request, hotel_id):
    hotel = Hotel.objects.filter(id=hotel_id).values().first()
    if not hotel:
        return JsonResponse({"error": "Hotel not found"}, status=404)
    return JsonResponse(hotel)


# =====================================================
# ROOM TYPES & AVAILABILITY
# =====================================================
def room_types_by_hotel(request, hotel_id):
    rooms = list(RoomType.objects.filter(hotel_id=hotel_id).values())
    return JsonResponse(rooms, safe=False)


def check_availability(request):
    availability = list(Availability.objects.values())
    return JsonResponse(availability, safe=False)


# =====================================================
# BOOKING LIST
# =====================================================
def booking_list(request):
    bookings = list(Booking.objects.values())
    return JsonResponse(bookings, safe=False)


# =====================================================
# INSTANT BOOKING (NON-DRF)
# =====================================================
@csrf_exempt
@transaction.atomic
def create_booking(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST

        room_type_id = int(data.get("room_type_id"))
        guest_name = data.get("guest_name")
        check_in = datetime.strptime(data.get("check_in"), "%Y-%m-%d").date()
        check_out = datetime.strptime(data.get("check_out"), "%Y-%m-%d").date()

    except Exception as e:
        return JsonResponse(
            {"error": "Invalid input data", "details": str(e)},
            status=400
        )

    if check_in >= check_out:
        return JsonResponse({"error": "Invalid date range"}, status=400)

    room_type = RoomType.objects.select_for_update().get(id=room_type_id)

    current = check_in
    while current < check_out:
        availability, _ = Availability.objects.get_or_create(
            room_type=room_type,
            date=current,
            defaults={"available_rooms": room_type.total_rooms}
        )
        if availability.available_rooms <= 0:
            return JsonResponse(
                {"error": f"No rooms available on {current}"},
                status=409
            )
        current += timedelta(days=1)

    current = check_in
    while current < check_out:
        availability = Availability.objects.select_for_update().get(
            room_type=room_type,
            date=current
        )
        availability.available_rooms -= 1
        availability.save()
        current += timedelta(days=1)

    booking = Booking.objects.create(
        room_type=room_type,
        guest_name=guest_name,
        check_in=check_in,
        check_out=check_out,
        amount=room_type.price,
        status="PENDING_PAYMENT"
    )

    return JsonResponse({
        "status": "PENDING_PAYMENT",
        "booking_id": booking.id
    }, status=201)


# =====================================================
# CANCEL BOOKING
# =====================================================
@csrf_exempt
@transaction.atomic
def cancel_booking(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
        booking_id = int(data.get("booking_id"))
    except Exception:
        return JsonResponse({"error": "Invalid input"}, status=400)

    booking = Booking.objects.select_for_update().filter(id=booking_id).first()
    if not booking:
        return JsonResponse({"error": "Booking not found"}, status=404)

    if booking.status == "CANCELLED":
        return JsonResponse({"error": "Already cancelled"}, status=400)

    current = booking.check_in
    while current < booking.check_out:
        availability = Availability.objects.select_for_update().get(
            room_type=booking.room_type,
            date=current
        )
        availability.available_rooms += 1
        availability.save()
        current += timedelta(days=1)

    booking.status = "CANCELLED"
    booking.save()

    return JsonResponse({
        "status": "CANCELLED",
        "booking_id": booking.id
    })


# =====================================================
# AVAILABILITY API (DRF)
# =====================================================
@api_view(["GET"])
def availability_api(request):

    try:
        room_type_id = int(request.query_params.get("room_type_id"))
        check_in = datetime.strptime(
            request.query_params.get("check_in"), "%Y-%m-%d"
        ).date()
        check_out = datetime.strptime(
            request.query_params.get("check_out"), "%Y-%m-%d"
        ).date()
    except Exception:
        return Response({"error": "Invalid input"}, status=400)

    room_type = RoomType.objects.filter(id=room_type_id).first()
    if not room_type:
        return Response({"error": "Invalid room_type_id"}, status=404)

    min_available = room_type.total_rooms
    dates = []

    current = check_in
    while current < check_out:
        availability, _ = Availability.objects.get_or_create(
            room_type=room_type,
            date=current,
            defaults={"available_rooms": room_type.total_rooms}
        )
        min_available = min(min_available, availability.available_rooms)
        dates.append({
            "date": str(current),
            "available_rooms": availability.available_rooms
        })
        current += timedelta(days=1)

    return Response({
        "room_type": room_type.name,
        "available": min_available > 0,
        "min_available_rooms": min_available,
        "date_wise_availability": dates
    })


# =====================================================
# DRF BOOKING (JWT PROTECTED)
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def drf_create_booking(request):

    serializer = BookingCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    with transaction.atomic():
        room_type = RoomType.objects.select_for_update().get(
            id=data["room_type_id"]
        )

        current = data["check_in"]
        while current < data["check_out"]:
            availability, _ = Availability.objects.get_or_create(
                room_type=room_type,
                date=current,
                defaults={"available_rooms": room_type.total_rooms}
            )
            if availability.available_rooms <= 0:
                return Response(
                    {"error": f"No rooms available on {current}"},
                    status=409
                )
            current += timedelta(days=1)

        current = data["check_in"]
        while current < data["check_out"]:
            availability = Availability.objects.select_for_update().get(
                room_type=room_type,
                date=current
            )
            availability.available_rooms -= 1
            availability.save()
            current += timedelta(days=1)

        booking = Booking.objects.create(
            room_type=room_type,
            guest_name=data["guest_name"],
            check_in=data["check_in"],
            check_out=data["check_out"],
            amount=room_type.price,
            status="PENDING_PAYMENT"
        )

    return Response({
        "status": "PENDING_PAYMENT",
        "booking_id": booking.id
    }, status=201)


# =====================================================
# PAYMENT INITIATION (IDEMPOTENT)
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def initiate_payment(request):

    booking_id = request.data.get("booking_id")
    idempotency_key = request.headers.get("Idempotency-Key")

    if not idempotency_key:
        return Response({"error": "Idempotency-Key required"}, status=400)

    booking = Booking.objects.select_for_update().get(id=booking_id)

    if booking.status != "PENDING_PAYMENT":
        return Response({"error": "Invalid booking state"}, status=400)

    payment, created = Payment.objects.get_or_create(
        idempotency_key=idempotency_key,
        defaults={
            "booking": booking,
            "status": "INITIATED"
        }
    )

    if not created:
        return Response({
            "razorpay_order_id": payment.razorpay_order_id,
            "idempotent": True
        })

    amount_paise = int(booking.room_type.price * 100)

    razorpay_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"booking_{booking.id}",
        "payment_capture": 1
    })

    payment.razorpay_order_id = razorpay_order["id"]
    payment.save()

    return Response({
        "razorpay_order_id": razorpay_order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key": settings.RAZORPAY_KEY_ID,
        "booking_id": booking.id
    })


# =====================================================
# PAYMENT CONFIRMATION
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def confirm_payment(request):

    booking_id = request.data.get("booking_id")
    success = request.data.get("success")

    booking = Booking.objects.select_for_update().get(id=booking_id)
    payment = booking.payment

    if booking.status != "PENDING_PAYMENT":
        return Response({"error": "Invalid payment state"}, status=400)

    if not success:
        booking.status = "PAYMENT_FAILED"
        payment.status = "FAILED"
        booking.save()
        payment.save()
        return Response({"status": "PAYMENT_FAILED"})

    booking.status = "CONFIRMED"
    payment.status = "SUCCESS"
    booking.save()
    payment.save()

    return Response({"status": "PAYMENT_SUCCESS"})


# =====================================================
# PAYMENT WEBHOOK (ASYNC)
# =====================================================
@csrf_exempt
@api_view(["POST"])
def razorpay_webhook(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return Response(
            {"error": "Invalid JSON (Webhook expects Razorpay payload)"},
            status=400
        )

    event = data.get("event")

    if event == "payment.captured":
        razorpay_order_id = data["razorpay_order_id"]

        payment = Payment.objects.get(
            razorpay_order_id=razorpay_order_id
        )

        payment.status = "SUCCESS"
        payment.save()

        booking = payment.booking
        booking.status = "CONFIRMED"
        booking.save()

        from .notifications import send_booking_confirmation
        send_booking_confirmation(booking)

    return Response({"status": "processed"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def refund_payment(request):

    booking_id = request.data.get("booking_id")
    booking = Booking.objects.select_for_update().get(id=booking_id)

    if booking.status != "CONFIRMED":
        return Response({"error": "Refund not allowed"}, status=400)

    booking.status = "REFUNDED"
    booking.save()

    return Response({"status": "REFUND_INITIATED"})

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def razorpay_create_order(request):

    booking_id = request.data.get("booking_id")
    booking = Booking.objects.select_for_update().get(id=booking_id)

    if booking.status != "PENDING_PAYMENT":
        return Response({"error": "Invalid state"}, status=400)

    if not booking.amount:
        return Response({"error": "Booking amount missing"}, status=400)

    payment = Payment.objects.filter(
        booking=booking,
        status="INITIATED"
    ).first()

    if payment:
        return Response({
            "order_id": payment.razorpay_order_id,
            "key": settings.RAZORPAY_KEY_ID,
            "amount": int(booking.amount * 100),
            "currency": "INR"
        })

    order = client.order.create({
        "amount": int(booking.amount * 100),
        "currency": "INR",
        "receipt": f"booking_{booking.id}",
        "payment_capture": 1
    })

    Payment.objects.create(
        booking=booking,
        razorpay_order_id=order["id"],
        status="INITIATED"
    )

    return Response({
        "order_id": order["id"],
        "key": settings.RAZORPAY_KEY_ID,
        "amount": order["amount"],
        "currency": "INR"
    })



@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def razorpay_verify_payment(request):

    data = request.data
    booking = Booking.objects.select_for_update().get(id=data["booking_id"])

    client.utility.verify_payment_signature({
        "razorpay_order_id": data["razorpay_order_id"],
        "razorpay_payment_id": data["razorpay_payment_id"],
        "razorpay_signature": data["razorpay_signature"]
    })

    booking.status = "CONFIRMED"
    booking.save()

    booking.payment.status = "SUCCESS"
    booking.payment.save()

    return Response({"status": "PAYMENT_SUCCESS"})


@csrf_exempt
@api_view(["POST"])
def razorpay_webhook(request):
    payload = json.loads(request.body)
    event = payload["event"]

    if event == "payment.failed":
        booking_id = payload["payload"]["payment"]["entity"]["notes"]["booking_id"]
        Booking.objects.filter(id=booking_id).update(status="PAYMENT_FAILED")

    return Response({"status": "ok"})

