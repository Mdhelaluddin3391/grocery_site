from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Hamara Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        # Ensure default role: if not provided, assume customer
        extra_fields.setdefault('is_customer', True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password) # Password ko hash karega
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Superusers are NOT customers
        extra_fields.setdefault('is_customer', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

# Hamara Custom User Model (Authentication ke liye)
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # NEW: explicit customer flag
    is_customer = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name'] # createsuperuser poochhega

    def __str__(self):
        return self.phone_number

# 1. Customer ke liye Profile Model
class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customerprofile')
    loyalty_points = models.IntegerField(default=0)
    # Aap yahan aur bhi fields add kar sakte hain, jaise date_of_birth

    def __str__(self):
        return f"Profile for customer: {self.user.name}"

# 2. Staff ke liye Profile Model
class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staffprofile')
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True) # e.g., 'Manager', 'Delivery Boy'

    def __str__(self):
        return f"Profile for staff: {self.user.name}"

# Address Model (User se linked)
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('Home', 'Home'),
        ('Office', 'Office'),
        ('Other', 'Other'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='Home')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    
    # Fields for location
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.get_address_type_display()} address for {self.user.phone_number}"
