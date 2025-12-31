# from django.http import JsonResponse
# from django.db import transaction
# from datetime import timedelta, datetime
#
# from .models import Hotel, RoomType, Booking, Availability
#
# @transaction.atomic
# def create_booking(request):
#     """
#     Expected POST params:
#     room_type_id
#     check_in  (YYYY-MM-DD)
#     check_out (YYYY-MM-DD)
#     guest_name
#     """
#
#     if request.method != "POST":
#         return JsonResponse({"error": "POST request required"}, status=400)
#
#     try:
#         room_type_id = int(request.POST.get("room_type_id"))
#         guest_name = request.POST.get("guest_name")
#         check_in = datetime.strptime(request.POST.get("check_in"), "%Y-%m-%d").date()
#         check_out = datetime.strptime(request.POST.get("check_out"), "%Y-%m-%d").date()
#     except Exception:
#         return JsonResponse({"error": "Invalid input data"}, status=400)
#
#     # 1️⃣ Validate dates
#     if check_in >= check_out:
#         return JsonResponse({"error": "Invalid date range"}, status=400)
#
#     room_type = RoomType.objects.select_for_update().get(id=room_type_id)
#
#     # 2️⃣ Generate date range
#     booking_dates = []
#     current_date = check_in
#     while current_date < check_out:
#         booking_dates.append(current_date)
#         current_date += timedelta(days=1)
#
#     # 3️⃣ Check availability for ALL dates
#     for day in booking_dates:
#         availability, created = Availability.objects.get_or_create(
#             room_type=room_type,
#             date=day,
#             defaults={"available_rooms": room_type.total_rooms},
#         )
#
#         if availability.available_rooms <= 0:
#             return JsonResponse(
#                 {
#                     "status": "FAILED",
#                     "reason": f"No rooms available on {day}",
#                 },
#                 status=409,
#             )
#
#     # 4️⃣ Reduce inventory (LOCKED by transaction)
#     for day in booking_dates:
#         availability = Availability.objects.select_for_update().get(
#             room_type=room_type,
#             date=day
#         )
#         availability.available_rooms -= 1
#         availability.save()
#
#     # 5️⃣ Create booking (AUTO-CONFIRM)
#     booking = Booking.objects.create(
#         room_type=room_type,
#         check_in=check_in,
#         check_out=check_out,
#         guest_name=guest_name,
#         status="CONFIRMED",
#     )
#
#     return JsonResponse(
#         {
#             "status": "CONFIRMED",
#             "booking_id": booking.id,
#             "room_type": room_type.name,
#             "check_in": check_in,
#             "check_out": check_out,
#         }
#     )


from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to GoExplorer 🚀")
