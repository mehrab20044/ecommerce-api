from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User,Profile

class CustomAdminPanel(UserAdmin):
    model= User
    list_display = ('phone_number','is_superuser','is_active','is_verified')
    list_filter =  ('phone_number','is_superuser','is_active','is_verified')
    search_fields = ('phone_number',)
    ordering = ('phone_number',)
    fieldsets = (
        ('Authentication',{
            'fields':(
                'phone_number','password'
            ),
        }),
        ('permissions',{
            'fields':(
                'is_active','is_staff','is_superuser','is_verified'
            ),
        }),
        ('group permissions',{
            'fields':(
                'groups','user_permissions'
            ),
        }),
        ('important date',{
            "fields":(
                'last_login',
            ),
        }),
    )

    add_fieldsets =(
        (None,{
            'classes':('wide',),
            'fields':('phone_number','email','password1','password2','is_staff','is_superuser','is_active')
        }),
    )




admin.site.register(User,CustomAdminPanel)
admin.site.register(Profile)