from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

# ✅ Allowed staff email domains
AUTHORIZED_STAFF_DOMAINS = ["gmail.com", "outlook.com"]  # Change as needed

class StaffSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Check if the social login email is from an authorized staff domain."""
        user = sociallogin.user
        email = sociallogin.account.extra_data.get('email')

        if not email:
            messages.error(request, "Google account did not return an email address.")
            raise ImmediateHttpResponse(redirect(settings.LOGIN_URL))

        email_domain = email.split('@')[-1].lower()

        # Check if this is an existing account
        if sociallogin.is_existing:
            if not user.is_staff:
                messages.error(request, "Access Denied: Your account is not authorized as staff.")
                raise ImmediateHttpResponse(redirect(settings.LOGIN_URL))
            return  # allow staff access

        # For new Google sign-ins
        if email_domain in AUTHORIZED_STAFF_DOMAINS:
            user.is_staff = True
            user.is_customer = False
            user.email = email
            user.username = email.split('@')[0]
            user.phone_number = ""  # staff doesn’t use phone login
            user.name = sociallogin.account.extra_data.get('name', 'Staff User')
        else:
            messages.error(request, f"Access Denied: '{email_domain}' is not an authorized staff domain.")
            raise ImmediateHttpResponse(redirect(settings.LOGIN_URL))

    def save_user(self, request, sociallogin, form=None):
        """Save the user after authorization."""
        user = super().save_user(request, sociallogin, form=form)
        user.save()
        return user
