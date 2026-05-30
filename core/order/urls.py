from django.urls import path,include


app_name="order"

urlpatterns=[
    path("api/v1/",include("order.api.v1.urls"))
]