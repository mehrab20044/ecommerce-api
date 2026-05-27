from django.urls import path, include
from .import views
from rest_framework_simplejwt.views import TokenRefreshSlidingView,TokenVerifyView

urlpatterns = [
    #registration
    path('register/',views.Registration.as_view(),name='register'),
    #change-password
    path('change-password/',views.ChangePasswordView.as_view(),name='change-password'),
    #jwt
    path('jwt/create',views.CustomTokenObtainPairView.as_view(), name='create'),
    path('jwt/refresh/',TokenRefreshSlidingView.as_view(),name='refresh'),
    path(
        "activation/confirm/<str:token>",
        views.ActivationApiView.as_view(),
        name="activation",
    ),
    path("activation/resend/", views.ActivationResendApiView.as_view(), name="resend"),
    # jwt
    path("jwt/create", views.CustomTokenObtainPairView.as_view(), name="create"),
    path("jwt/refresh/", TokenRefreshSlidingView.as_view(), name="refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="verify"),

    path('jwt/verify/',TokenVerifyView.as_view(),name='verify'),
    #profile
    path('profile/',views.ProfileView.as_view(),name='profile'),
]