from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # UI routes
    path("", include("booking.urls_ui")),

    # API routes
    path("api/", include("booking.urls_api")),
]
