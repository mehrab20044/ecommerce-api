from django.db import models
from django.contrib.auth.models import (PermissionsMixin,AbstractBaseUser,BaseUserManager)
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.validators import validate_iranian_cellphone_number

class UserManager(BaseUserManager):
    '''
    custom user model manager where email is the unique identifiers for authentication instead of usernames.
    '''
    def create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError("Email not valid")
        
        email= self.normalize_email(email)
        user =self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_verified',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError ('user not staff')
        elif extra_fields.get('is_superuser') is not True:
            raise ValueError('user is not VIP')
        return self.create_user(email,password,**extra_fields)

        


class User(AbstractBaseUser,PermissionsMixin):
    '''
    custom user model for our app
    '''
    email = models.EmailField(max_length=255,unique=True)
    is_superuser= models.BooleanField(default=False)
    is_active= models.BooleanField(default=True)
    is_staff= models.BooleanField(default=False)
    is_verified= models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    create_date=models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


    objects=UserManager()
    def __str__(self):
        return self.email
    

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    image= models.ImageField(blank=True,null=True)
    phone_number = models.CharField(max_length=12, validators=[validate_iranian_cellphone_number])   
    description = models.TextField()

    create_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    
    def get_fullname(self):
        if self.first_name or self.last_name:
            return self.first_name + " " + self.last_name
        return "کاربر جدید"
    
    @receiver(post_save,sender=User)
    def save_profile(sender,instance,created,**kwargs):
        if created:
            Profile.objects.create(user=instance)