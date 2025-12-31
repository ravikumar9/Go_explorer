from django.urls import path
from . import views_ui

urlpatterns = [
    path("", views_ui.home, name="home"),
    path("hotels/", views_ui.hotels_list, name="hotels_list"),
    path("rooms/<int:hotel_id>/", views_ui.rooms_list, name="rooms_list"),
    path("review/", views_ui.review_booking, name="review_booking"),
    path("booking/create/", views_ui.create_booking, name="create_booking"),

    path("payment/<int:booking_id>/", views_ui.payment_page, name="payment_page"),
    path("payment/success/", views_ui.payment_success, name="payment_success"),
]
