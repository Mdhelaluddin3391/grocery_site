# accounts/models.py (FINAL CODE: Customer/Admin Isolation)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings 
# UserManager import hata diya gaya hai
# Backends import hata diya gaya hai

# --- 1. ADMIN USER MODEL (The AUTH_USER_MODEL) ---
# Yeh model sirf Django Admin/Superuser login ke liye hai.
class User(AbstractUser):
    # phone_number sirf data ke liye rakha gaya hai
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # objects = UserManager() reference hata diya gaya hai
    
    def __str__(self):
        # Admin ke liye username
        return self.username or f"Admin/Staff ({self.pk})"

# --- 2. CUSTOMER MODEL (The Web User) ---
# Yeh model completely independent hai aur customer data rakhega.
class Customer(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.phone_number

# --- 3. ADDRESS MODEL (Now linked to Customer) ---
class Address(models.Model):
    ADDRESS_CHOICES = (
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    )

    # Foreign Key ab Customer model ko point karta hai
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    address_type = models.CharField(max_length=50, choices=ADDRESS_CHOICES, default='Home')
    is_default = models.BooleanField(default=False)
    
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    def __str__(self):
        return f"{self.customer.phone_number}'s {self.address_type} Address"

    class Meta:
        verbose_name_plural = "Addresses"

# --- 4. OTP MODEL (Linked to Customer flow) ---
class OTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.phone_number}"