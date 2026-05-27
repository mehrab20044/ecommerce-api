from django.urls import path, include

urlpatterns = [
    path("api/v1/", include("cart.api.v1.urls")),
]
