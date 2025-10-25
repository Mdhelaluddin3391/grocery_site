# accounts/admin.py (FINAL CODE: Registering both User and Customer)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Customer, Address, OTP

# Custom Admin for the AUTH_USER_MODEL (Admin/Staff)
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # Admin ke liye fields jo AbstractUser se aate hain
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)
    
# Custom Admin for the Customer Model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'is_verified', 'created_at')
    search_fields = ('phone_number',)
    list_filter = ('is_verified',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    # Foreign key is now customer
    list_display = ('customer', 'address_line_1', 'city', 'pincode', 'address_type', 'is_default')
    list_filter = ('address_type', 'is_default', 'city')
    search_fields = ('customer__phone_number', 'address_line_1', 'pincode')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp_code', 'created_at')
    search_fields = ('phone_number',)