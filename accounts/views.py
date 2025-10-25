from django.shortcuts import render

# Create your views here.
# accounts/views.py (FINAL CODE)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from .forms import PhoneNumberForm, OTPVerificationForm
from .models import User, OTP, Address
from store.views import get_main_categories
import random
import time 

# Django's default User model ki jagah hamara custom User model
User = get_user_model()


# Helper function to simulate OTP sending
def send_otp(phone_number, otp_code):
    """
    OTP bhejane ka simulation. Production mein yahan SMS API ka code aayega.
    """
    print(f"--- OTP SENT ---")
    print(f"To: {phone_number}, Code: {otp_code}")
    print(f"----------------")
    # messages.info(request, f"Your OTP is {otp_code}. (Demo Mode)") # Optional for demo

def generate_otp():
    return str(random.randint(100000, 999999))


def phone_login(request):
    """
    Step 1: User se phone number lena aur OTP generate/send karna.
    """
    if request.user.is_authenticated:
        return redirect('profile')

    form = PhoneNumberForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        phone_number = form.cleaned_data['phone_number']
        
        # 1. OTP generate karein
        otp_code = generate_otp()
        
        # 2. OTP ko DB mein save/update karein (ya create karein)
        otp_obj, created = OTP.objects.update_or_create(
            phone_number=phone_number,
            defaults={'otp_code': otp_code}
        )
        
        # 3. OTP bhejein (Simulated)
        send_otp(phone_number, otp_code)
        
        # 4. OTP verification page par redirect karein
        request.session['phone_for_otp'] = phone_number # Session mein phone number store karein
        messages.success(request, f"OTP sent to {phone_number}. Please verify.")
        return redirect('otp_verify')

    context = {
        'form': form,
        'main_categories': get_main_categories(),
    }
    return render(request, 'accounts/login.html', context)


def otp_verify(request):
    """
    Step 2: User se OTP lena aur login/registration complete karna.
    """
    phone_number = request.session.get('phone_for_otp')
    if not phone_number:
        messages.error(request, "OTP process failed. Please re-enter your phone number.")
        return redirect('login')

    form = OTPVerificationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user_otp = form.cleaned_data['otp']
        
        # 1. DB se OTP check karein
        try:
            otp_obj = OTP.objects.get(phone_number=phone_number)
        except OTP.DoesNotExist:
            messages.error(request, "Invalid phone number or OTP expired. Try again.")
            return redirect('login')

        # 2. OTP aur time check karein (Basic expiry check: 5 minutes)
        if otp_obj.otp_code == user_otp and (time.time() - otp_obj.created_at.timestamp()) < 300:
            
            # 3. User ko find ya create karein
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={'is_active': True, 'is_verified': True}
            )

            # 4. Login karein
            login(request, user, backend='accounts.backends.PhoneBackend')
            otp_obj.delete() # OTP use hone ke baad delete kar dein
            
            # 5. Redirect karein
            if created:
                messages.success(request, "Registration successful! Welcome to QuickDash.")
            else:
                messages.success(request, "Login successful! Welcome back.")
            
            # Session se phone number hata dein
            del request.session['phone_for_otp'] 
            
            return redirect('profile')

        else:
            messages.error(request, "Invalid or expired OTP.")
    
    context = {
        'form': form,
        'phone_number': phone_number,
        'main_categories': get_main_categories(),
    }
    return render(request, 'accounts/otp_verify.html', context)


@login_required
def profile_view(request):
    """
    User ka profile page jahan se woh apne orders aur details dekh sakta hai.
    """
    # Cart app mein Address model ka reference hai, isliye yahan import karna zaroori hai.
    try:
        user_addresses = Address.objects.filter(user=request.user)
    except Exception:
        user_addresses = []

    context = {
        'user': request.user,
        'addresses': user_addresses,
        'main_categories': get_main_categories(),
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def user_logout(request):
    """
    User ko log out karein.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def delete_account(request):
    """
    User ka account aur usse jude sabhi data (orders, cart, addresses) delete karein.
    """
    if request.method == 'POST':
        user = request.user
        
        # User se jude saare objects (Cart, Order, Address) CASCADE ho jayenge
        # kyunki hamare models mein on_delete=models.CASCADE set hai.
        # Agar aap sab kuch delete karna chahte hain to User object ko delete kar dein.
        
        # Pehle user ko logout karein
        logout(request)
        
        # Ab User object ko delete karein
        user.delete() 

        messages.success(request, "Your account has been permanently deleted, along with all associated data.")
        return redirect('home')
        
    return render(request, 'accounts/delete_confirm.html', {'main_categories': get_main_categories()})