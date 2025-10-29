# dashboard/staff_social_adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages

class StaffSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        ✅ UPDATED: Ab yeh hamesha False return karega.
        Iska matlab hai ki har naye Google user ko sign-up form bharna padega.
        """
        return False

    def pre_social_login(self, request, sociallogin):
        """
        Yeh method naye user ko staff ke roop mein set up karta hai.
        """
        # Purane non-staff users ko block karein
        if sociallogin.is_existing and not sociallogin.user.is_staff:
            messages.error(request, "Access Denied: Aapka account staff ke roop mein authorized nahi hai.")
            raise ImmediateHttpResponse(redirect('staff_login'))

        # Naye users ke liye, staff details automatically set karein
        if not sociallogin.is_existing:
            user = sociallogin.user
            user.is_staff = True
            user.is_customer = False
            user.email = sociallogin.account.extra_data.get('email')
            user.name = sociallogin.account.extra_data.get('name', 'Staff User')

    def save_user(self, request, sociallogin, form=None):
        """User ke account ko save karta hai."""
        # Hum password form mein save kar rahe hain, isliye yahan kuch khaas karne ki zaroorat nahi.
        return super().save_user(request, sociallogin, form)