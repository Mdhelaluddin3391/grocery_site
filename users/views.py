# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth import get_user_model, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views import View
import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PhoneOTP, CustomerProfile, StaffProfile



User = get_user_model()


def otp_login_page(request):
    """Show phone number input page."""
    return render(request, 'users/login.html')

    
# -------------------- SEND OTP --------------------
@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')

        if not phone:
            return JsonResponse({'status': 'error', 'message': 'Phone number is required'})

        otp_code = PhoneOTP.generate_otp()
        PhoneOTP.objects.update_or_create(phone=phone, defaults={'otp': otp_code, 'created_at': timezone.now(), 'tries': 0})

        # Simulate sending OTP (in real setup use Twilio or other SMS gateway)
        print(f"OTP for {phone} is {otp_code}")

        return JsonResponse({'status': 'success', 'message': f'OTP sent to {phone}'})


# -------------------- VERIFY OTP --------------------
@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        otp_input = request.POST.get('otp')

        try:
            otp_record = PhoneOTP.objects.get(phone=phone)
        except PhoneOTP.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'No OTP found for this phone number'})

        if otp_record.is_expired():
            otp_record.delete()
            return JsonResponse({'status': 'error', 'message': 'OTP expired, please request again'})

        if otp_input != otp_record.otp:
            otp_record.tries += 1
            otp_record.save()
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})

        # OTP verified successfully
        otp_record.delete()

        # Create or get user and ensure they are marked as a customer.
        user, _ = User.objects.get_or_create(phone_number=phone)
        if not user.is_customer:
            user.is_customer = True
            user.save()

        # THIS IS THE KEY: Ensure a customer profile exists.
        # It creates one if it's missing, or does nothing if it already exists.
        CustomerProfile.objects.get_or_create(user=user)

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return JsonResponse({'status': 'success', 'message': 'Login successful'})

# -------------------- LOGOUT --------------------
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('/')


# -------------------- CUSTOMER PROFILE --------------------
@login_required(login_url='/login/')
def profile_view(request):
    """
    This profile view is ONLY for customers who log in via OTP.
    """
    # Check if the logged-in user has a customer profile.
    profile = getattr(request.user, 'customerprofile', None)

    if profile:
        # If they have a customer profile, show the page.
        return render(request, 'users/customer_profile.html', {'profile': profile})
    else:
        # If the logged-in user is not a customer (e.g., they are staff or a superuser),
        # they should not be on this page. Redirect them away.
        messages.error(request, "This profile page is for customers only.")
        return redirect('home')


# -------------------- STAFF GOOGLE LOGIN HANDLER --------------------
from allauth.socialaccount.models import SocialAccount

@login_required
def google_login_success(request):
    """
    This view runs only for Google Sign-In users (staff/admin).
    """
    if not request.user.is_staff:
        logout(request)
        messages.error(request, "Access denied. You are not a staff member.")
        return redirect('/')

    social_account = SocialAccount.objects.filter(user=request.user).first()
    if social_account:
        StaffProfile.objects.get_or_create(user=request.user)
        messages.success(request, f"Welcome back, {request.user.username} (Google Login)!")
        return redirect('/admin-dashboard/')
    else:
        logout(request)
        messages.error(request, "Google authentication failed.")
        return redirect('/')
