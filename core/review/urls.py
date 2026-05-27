from django.urls import path ,include

app_name= "review"

urlpatterns=[
    path("api/v1/", include("review.api.v1.urls")),
]