from accounts.models import User,Profile
from .serializers import RegistrationSerializers,CustomTokenObtainPairSerializer,ChangePasswordSerializers,ProfileSerializers,ActivationResendSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views  import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
import jwt
from django.conf import settings
from rest_framework.views import APIView

class Registration(generics.GenericAPIView):
    serializer_class=RegistrationSerializers

    def post(self, request, *args, **kwargs):
        serializer=RegistrationSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {"email": email}
            user_obj = get_object_or_404(User, email=email)
            token = self.get_tokens_for_user(user_obj)

            body = render_to_string("email/hello.html", {"token": token})

            email_obj = EmailMessage(
                subject="Hello", body=body, from_email="admin@admin.com", to=[email]
            )
            email_obj.content_subtype = "html"
            email_obj.send()
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class=CustomTokenObtainPairSerializer


class ChangePasswordView(generics.GenericAPIView):
    serializer_class= ChangePasswordSerializers
    model= User
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = self.request.user
        return obj
   
    def put(self, request, *args, **kwargs):
        self.object=self.get_object()
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get('old_password')):
                raise Response({'old_password':['Wrong password']},status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({'detail':'change password successfuly'},status=status.HTTP_200_OK)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class=ProfileSerializers
    queryset= Profile.objects.all()

    def get_object(self):
        queryset=self.get_queryset()
        obj = get_object_or_404(queryset,user=self.request.user)
        return obj
    

class ActivationApiView(APIView):
    def get(self, request, token, *args, **kwargs):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = token.get("user_id")
        except ExpiredSignatureError:
            return Response(
                {"details": "token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidSignatureError:
            return Response(
                {"details": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_obj = User.objects.get(pk=user_id)

        if user_obj.is_verified:
            return Response({"details": "account already activated"})
        user_obj.is_verified = True
        user_obj.save()
        return Response(
            {"details": "your account have been verified and activated successfully"},
            status=status.HTTP_200_OK,
        )
            

class ActivationResendApiView(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = ActivationResendSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user_obj = serializer.validated_data["user"]
            token = self.get_tokens_for_user(user_obj)

            body = render_to_string("email/hello.html", {"token": token})

            email_obj = EmailMessage(
                subject="Hello", body=body, from_email="admin@admin.com", to=[email]
            )
            email_obj.content_subtype = "html"
            email_obj.send()

            return Response({"message": "email sent"})

        else:
            return Response(
                {"details": "request failed"}, status=status.HTTP_400_BAD_REQUEST
            )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
