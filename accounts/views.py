# accounts/views.py (FINAL CODE: Custom Customer Auth)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout # Django auth logout
from django.contrib import messages
from .forms import PhoneNumberForm, OTPVerificationForm
from .models import User, Customer, OTP, Address 
from store.views import get_main_categories
import random
import time 

# --- CUSTOMER AUTH CHECK DECORATOR ---
def customer_login_required(view_func):
    """Decorator to ensure a Customer is logged in via session and blocks Admin users."""
    def wrapper(request, *args, **kwargs):
        # 1. Admin Block: Django's default auth check
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
             messages.warning(request, "Staff accounts cannot access customer profile views.")
             return redirect('home')

        # 2. Customer Auth: Custom session check
        if 'customer_id' not in request.session:
            messages.info(request, "Please log in to access your profile.")
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper
# ------------------------------------

# Helper functions...
def send_otp(phone_number, otp_code):
    print(f"--- OTP SENT ---")
    print(f"To: {phone_number}, Code: {otp_code}")
    print(f"----------------")
def generate_otp():
    return str(random.randint(100000, 999999))


def phone_login(request):
    """
    Customer login ka Step 1: Phone number aur OTP request.
    """
    if 'customer_id' in request.session:
        return redirect('profile')
    
    # Admin is already logged in as Django user, but accessing customer login
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('home')

    form = PhoneNumberForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        phone_number = form.cleaned_data['phone_number']
        
        # Customer user ko create ya retrieve karein
        customer, created = Customer.objects.get_or_create(phone_number=phone_number)
        
        otp_code = generate_otp()
        
        OTP.objects.update_or_create(
            phone_number=phone_number,
            defaults={'otp_code': otp_code}
        )
        
        send_otp(phone_number, otp_code)
        
        request.session['phone_for_otp'] = phone_number 
        request.session['customer_to_verify_id'] = customer.id 
        messages.success(request, f"OTP sent to {phone_number}. Please verify.")
        return redirect('otp_verify')

    context = {
        'form': form,
        'main_categories': get_main_categories(),
    }
    return render(request, 'accounts/login.html', context)


def otp_verify(request):
    """
    Customer login ka Step 2: OTP verification aur manual session set karna.
    """
    phone_number = request.session.get('phone_for_otp')
    customer_id = request.session.get('customer_to_verify_id')
    
    if not phone_number or not customer_id:
        messages.error(request, "OTP process failed. Please re-enter your phone number.")
        return redirect('login')

    form = OTPVerificationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user_otp = form.cleaned_data['otp']
        
        try:
            otp_obj = OTP.objects.get(phone_number=phone_number)
        except OTP.DoesNotExist:
            messages.error(request, "Invalid phone number or OTP expired. Try again.")
            return redirect('login')

        if otp_obj.otp_code == user_otp and (time.time() - otp_obj.created_at.timestamp()) < 300:
            
            customer = get_object_or_404(Customer, id=customer_id)
            customer.is_verified = True
            customer.save()
            
            # --- CUSTOMER SESSION MANAGEMENT (MANUAL) ---
            request.session['customer_id'] = customer.id 
            # --------------------------------------------
            
            otp_obj.delete() 
            
            del request.session['phone_for_otp'] 
            del request.session['customer_to_verify_id']
            
            messages.success(request, "Login successful! Welcome back.")
            return redirect('profile')

        else:
            messages.error(request, "Invalid or expired OTP.")
    
    context = {
        'form': form,
        'phone_number': phone_number,
        'main_categories': get_main_categories(),
    }
    return render(request, 'accounts/otp_verify.html', context)


@customer_login_required 
def profile_view(request):
    """
    Customer profile page.
    """
    customer = get_object_or_404(Customer, id=request.session['customer_id'])
    
    try:
        user_addresses = Address.objects.filter(customer=customer)
    except Exception:
        user_addresses = []

    context = {
        'customer': customer,
        'addresses': user_addresses,
        'main_categories': get_main_categories(),
    }
    return render(request, 'accounts/profile.html', context)


def customer_logout(request):
    """
    Customer logout aur Admin user ko bhi log out karein agar woh authenticated ho.
    """
    if 'customer_id' in request.session:
        del request.session['customer_id']
        messages.info(request, "You have been logged out.")
    
    # Agar Admin user accidentally web app se log out kar raha hai
    if request.user.is_authenticated:
        auth_logout(request)
        
    return redirect('home')


@customer_login_required 
def delete_account(request):
    """
    Customer account deletion.
    """
    customer = get_object_or_404(Customer, id=request.session['customer_id'])
    
    if request.method == 'POST':
        customer_logout(request)
        customer.delete() 

        messages.success(request, "Your account has been permanently deleted, along with all associated data.")
        return redirect('home')
        
    return render(request, 'accounts/delete_confirm.html', {'main_categories': get_main_categories()})