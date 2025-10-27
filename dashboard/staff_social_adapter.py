# dashboard/staff_social_adapter.py (NEW FILE)

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

# --- AUTHORIZED STAFF DOMAINS ---
# Yahan woh email domain likhein jinke users ko staff access milega.
AUTHORIZED_STAFF_DOMAINS = ["your-company-domain.com", "example.com"] 
# Example: Agar aapke staff ki emails '@myshop.com' se hain, toh ["myshop.com"] likhein.

class StaffSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        email = sociallogin.account.extra_data.get('email')
        
        if not email:
            messages.error(request, "Google account does not provide an email address.")
            raise ImmediateHttpResponse(redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL))
            
        email_domain = email.split('@')[-1].lower()
        is_authorized = email_domain in AUTHORIZED_STAFF_DOMAINS
        
        if sociallogin.is_existing:
            # Existing user: Sirf staff members ko allow karein
            if not user.is_staff:
                messages.error(request, "Access Denied: Your existing account is not authorized for staff dashboard.")
                raise ImmediateHttpResponse(redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL))
        else:
            # Naya user: Domain check karein aur staff bana dein
            if is_authorized:
                # User ko staff aur non-customer bana dein
                user.is_staff = True
                user.is_customer = False 
                # Humara CustomUser model phone_number use karta hai, isliye isse email se populate kar dein
                user.phone_number = email
                if not user.name:
                    user.name = sociallogin.account.extra_data.get('name', 'Staff User')
            else:
                # Unauthorized domain ko block karein
                messages.error(request, f"Access Denied: Email domain '{email_domain}' is not authorized for staff sign-up.")
                raise ImmediateHttpResponse(redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL))

    def save_user(self, request, sociallogin, form=None):
        # Base save_user call karein jo user ko save karta hai aur socialaccount objects banata hai
        user = super().save_user(request, sociallogin, form=form)
        return user