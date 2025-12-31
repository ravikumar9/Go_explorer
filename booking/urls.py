from django.urls import path, include

urlpatterns = [
    path("", include("booking.urls_ui")),        # UI
    path("api/", include("booking.urls_api")),   # API
]
