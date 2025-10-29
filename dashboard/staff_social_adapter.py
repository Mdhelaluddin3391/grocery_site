# dashboard/staff_social_adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from .models import AuthorizedStaff # Import the database model

# Company-wide domains are still checked here
AUTHORIZED_STAFF_DOMAINS = ["quickdash.com"]

class StaffSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        ✅ New Method: This is the key to skipping the sign-up form.
        It checks if a new user is authorized BEFORE showing any page.
        """
        email = sociallogin.account.extra_data.get('email', '').lower()
        if not email:
            return False # Block if no email is provided

        # Check authorization from both the domain list and the database
        email_domain = email.split('@')[-1]
        is_authorized_domain = email_domain in AUTHORIZED_STAFF_DOMAINS
        is_authorized_email = AuthorizedStaff.objects.filter(email=email).exists()

        # If authorized by either method, allow automatic sign-up
        return is_authorized_email or is_authorized_domain

    def pre_social_login(self, request, sociallogin):
        """
        This method now prepares the user's account details after the
        auto-signup check has already approved them.
        """
        # Block existing non-staff users
        if sociallogin.is_existing and not sociallogin.user.is_staff:
            messages.error(request, "Access Denied: Your account is not authorized as staff.")
            raise ImmediateHttpResponse(redirect('staff_login'))

        # For new users, populate their staff details automatically
        if not sociallogin.is_existing:
            # We double-check authorization here for extra security
            if not self.is_auto_signup_allowed(request, sociallogin):
                messages.error(request, f"Access Denied: Your email is not authorized for staff access.")
                raise ImmediateHttpResponse(redirect('staff_login'))
            else:
                # Set up the new user as a staff member
                user = sociallogin.user
                user.is_staff = True
                user.is_customer = False
                user.email = sociallogin.account.extra_data.get('email')
                # user.username = user.email.split('@')[0]
                user.name = sociallogin.account.extra_data.get('name', 'Staff User')

    def save_user(self, request, sociallogin, form=None):
        """Saves the user's account."""
        user = sociallogin.user
        if not user.pk:
            # Staff do not use phone numbers for login
            user.phone_number = None
        
        # Let allauth handle the final saving process
        return super().save_user(request, sociallogin, form)