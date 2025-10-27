# dashboard/staff_social_adapter.py (FULLY UPDATED)

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

# --- APNA STAFF EMAIL DOMAIN YAHAN LIKHEIN ---
# Example: Agar aapke staff ki emails '@mycompany.com' se hain, toh ["mycompany.com"] likhein.
AUTHORIZED_STAFF_DOMAINS = ["gmail.com", "outlook.com"] # <-- Ise apne domain se badlein

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
                # --- YEH UPDATE HUYA HAI ---
                # User ko staff aur non-customer bana dein
                user.is_staff = True
                user.is_customer = False
                # -------------------------
                
                user.email = email
                # Phone number ko abhi ke liye unique hone ke liye email se set kar rahe hain
                user.phone_number = email

                if not user.name:
                    user.name = sociallogin.account.extra_data.get('name', 'Staff User')
            else:
                messages.error(request, f"Access Denied: Email domain '{email_domain}' is not authorized.")
                raise ImmediateHttpResponse(redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL))

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        return user