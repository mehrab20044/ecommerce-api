from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshSlidingView,TokenVerifyView
from .views import SendOTPview, VerifyOTPview,Registration,ProfileView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .views import CustomTokenObtainPairView,ChangePasswordView,ActivationApiView,ActivationResendApiView
urlpatterns = [
    #registration
    path('register/',Registration.as_view(),name='register'),
    #change-password
    path('change-password/',ChangePasswordView.as_view(),name='change-password'),
    #jwt
    path('jwt/create',CustomTokenObtainPairView.as_view(), name='create'),
    path('jwt/refresh/',TokenRefreshSlidingView.as_view(),name='refresh'),
    path(
        "activation/confirm/<str:token>",
        ActivationApiView.as_view(),
        name="activation",
    ),
    path("activation/resend/", ActivationResendApiView.as_view(), name="resend"),
    # jwt
    path("jwt/create",  CustomTokenObtainPairView.as_view(), name="create"),
    path("jwt/refresh/", TokenRefreshSlidingView.as_view(), name="refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="verify"),

    path('jwt/verify/',TokenVerifyView.as_view(),name='verify'),
    #profile
    path('profile/', ProfileView.as_view(),name='profile'),
    # otp
    path("otp/send/", SendOTPview.as_view(), name="send-otp"),
    path("otp/verify/", VerifyOTPview.as_view(), name="verify-otp"),
]