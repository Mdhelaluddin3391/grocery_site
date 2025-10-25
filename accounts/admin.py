# accounts/admin.py (FINAL CODE)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address, OTP

# Custom Admin Form for our User Model
class CustomUserAdmin(BaseUserAdmin):
    # Fieldsets for superuser management in Django Admin
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}), # phone_number ko top par rakhein
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # List view settings
    list_display = ('phone_number', 'email', 'first_name', 'is_staff', 'is_verified')
    search_fields = ('phone_number', 'email')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    # Username field ko hata diya hai, isliye isko exclude karna padega
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'is_verified')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line_1', 'city', 'pincode', 'address_type', 'is_default')
    list_filter = ('address_type', 'is_default', 'city')
    search_fields = ('user__phone_number', 'address_line_1', 'pincode')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp_code', 'created_at')
    search_fields = ('phone_number',)

# Hamara Custom User model register karein
admin.site.register(User, CustomUserAdmin)