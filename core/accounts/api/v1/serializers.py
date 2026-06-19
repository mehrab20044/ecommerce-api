from rest_framework import serializers 
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import User,Profile 

class RegistrationSerializers(serializers.ModelSerializer):
    password1= serializers.CharField(write_only = True)

    class Meta:
        model=User
        fields=['email','password','password1']

    def validate(self, attrs):
        if attrs.get('password')!= attrs.get("password1"):
            raise serializers.ValidationError({'detail':'password doesn`t mach'})
        try:
            validate_password(attrs.get('password'))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        return super().validate(attrs)
    def create(self, validated_data):
        validated_data.pop('password1',None)
        return User.objects.create_user(**validated_data)
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
        def validate(self, attrs):
            validated_data =  super().validate(attrs)
            if not self.user.is_verified:
                raise serializers.ValidationError({'details':'user is not verified'})
            validated_data['email'] = self.user.email
            validated_data['user_id'] = self.user.id
            return validated_data

class ChangePasswordSerializers(serializers.Serializer):
    old_password=serializers.CharField(required=True)
    new_password=serializers.CharField(required=True)
    new_password1=serializers.CharField(required=True)
    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError({"detail":"password not mach"})
        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password':list(e.message)})
        return super().validate(attrs)
    
class ProfileSerializers(serializers.ModelSerializer):
    email=serializers.CharField(source='user.email',read_only=True)

    class Meta:
        model = Profile
        fields=fields=['id','email','first_name','last_name','image','description']
        read_only_fields = ['email']



class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "user does not exist"})

        if user_obj.is_verified:
            raise serializers.ValidationError(
                {"detail": "user is already activated and verified"}
            )

        attrs["user"] = user_obj
        return super().validate(attrs)
    
class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11,min_length=11)

    def validate_phone_number(self, value):
        if not value.isdigit() or not value.startswith('09'):
            raise serializers.ValidationError("Invalid phone number format. It should be 11 digits and start with '09'.")
        return value
class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11,min_length=11)
    otp_code = serializers.CharField(max_length=6)