# accounts/models.py (FINAL CODE: Supporting dual authentication)

from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager # Custom Manager import karein

# --- CUSTOM USER MODEL ---
class User(AbstractUser):
    # AbstractUser se 'username' field ab Admin/Staff ke liye upalabdh hai.
    # Humne 'username = None' hata diya hai.
    
    # Customer login ke liye field. Admin ke liye yeh optional rahega.
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False) # OTP verification ke liye

    # Admin/Staff login ke liye: 'username' field (AbstractUser se aayega) ka istemal karein
    USERNAME_FIELD = 'username' 
    # Superuser/Staff creation mein sirf username aur password required honge (Django default).
    REQUIRED_FIELDS = [] 

    objects = UserManager() # Custom manager use karein

    def __str__(self):
        # Admin ke liye username dikhega, Customer ke liye phone_number
        if self.is_staff or self.is_superuser:
            return self.username
        return self.phone_number or self.username

# --- ADDRESS MODEL (used in cart/views.py) ---
class Address(models.Model):
    ADDRESS_CHOICES = (
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    address_type = models.CharField(max_length=50, choices=ADDRESS_CHOICES, default='Home')
    is_default = models.BooleanField(default=False)
    
    # Checkout ke liye latitude/longitude fields
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username or self.user.phone_number}'s {self.address_type} Address"

    class Meta:
        verbose_name_plural = "Addresses"

# --- OTP MODEL ---
class OTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.phone_number}"