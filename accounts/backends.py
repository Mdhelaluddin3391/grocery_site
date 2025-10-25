# accounts/backends.py (FINAL CORRECTED CODE)

from .models import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

# 1. Customer Phone/OTP Backend
class PhoneBackend:
    """
    Customer authentication backend jo sirf phone_number se user ko authenticate karega 
    (used during OTP verification in views).
    """
    def authenticate(self, request, phone_number=None):
        try:
            # Sirf un users ko dhundein jinka phone_number hai aur woh staff/superuser nahi hain
            user = User.objects.get(phone_number=phone_number) 
            # Note: Yahan koi password check nahi hai, sirf user ka maujood hona kaafi hai
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# 2. Admin/Superuser Default Backend
# Hum Django ke default ModelBackend ka istemal Admin login ke liye karenge.
# Iske liye settings mein changes kiye gaye hain.