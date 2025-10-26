# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

# --- 1. ADMIN USER MODEL (The AUTH_USER_MODEL) ---
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # --- YEH BADLAV KIYE GAYE HAIN ---
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set", # Alag related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions_set", # Alag related_name
        related_query_name="user",
    )
    # ---------------------------------
    
    def __str__(self):
        return self.username or f"Admin/Staff ({self.pk})"

# --- 2. CUSTOMER MODEL ---
class Customer(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.phone_number

# --- 3. ADDRESS MODEL ---
class Address(models.Model):
    ADDRESS_CHOICES = (('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other'))
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

# --- 4. OTP MODEL ---
class OTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.phone_number}"