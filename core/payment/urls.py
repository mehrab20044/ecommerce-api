from django.urls import path , include

app_name= "payment"

urlpatterns = [
    path("api/v1/", include("payment.api.v1.urls")),
]