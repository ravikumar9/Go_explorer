from django.urls import path
from . import views

urlpatterns = [
    path("", views.api_root),

    path("hotels/", views.hotel_list),
    path("hotels/<int:hotel_id>/", views.hotel_detail),

    path("rooms/<int:hotel_id>/", views.room_types_by_hotel),
    path("availability/", views.availability_api),

    path("booking/create/", views.create_booking),
    path("booking/cancel/", views.cancel_booking),

    # 🔐 Razorpay APIs
    path("payment/initiate/", views.initiate_payment),
    path("payment/create-order/", views.razorpay_create_order),
    path("payment/verify/", views.razorpay_verify_payment),
    path("payment/webhook/", views.razorpay_webhook),
]
