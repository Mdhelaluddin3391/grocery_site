# mdhelaluddin3391/grocery_site/grocery_site-b7c9b0ae8a697f4fa8e0b4620ececbe3ab919e2a/accounts/views.py

import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction

# Zaroori Forms aur Models ko import karein
from .forms import (
    PhoneNumberForm, 
    OTPForm, 
    AddressForm, 
    UserUpdateForm, 
    UserProfileUpdateForm
)
from .models import UserProfile, Address
from cart.models import Order


# --- Naya Phone Number + OTP Login/Signup System ---

def phone_login(request):
    """User se phone number leta hai aur OTP bhejta hai."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            otp = random.randint(100000, 999999)
            
            print(f" OTP for {phone_number} is {otp} ")
            
            request.session['phone_number'] = phone_number
            request.session['otp'] = otp
            
            messages.info(request, 'An OTP has been sent. Please check the console.')
            return redirect('verify_otp')
    else:
        form = PhoneNumberForm()
    return render(request, 'accounts/phone_login.html', {'form': form})


# --- YEH VIEW POORI TARAH SE UPDATE KIYA GAYA HAI ---
@transaction.atomic # Database operations ko safe rakhne ke liye
def verify_otp(request):
    """User se OTP leta hai, verify karta hai, aur login/create karta hai."""
    if request.user.is_authenticated:
        return redirect('home')

    phone_number = request.session.get('phone_number')
    session_otp = request.session.get('otp')

    if not phone_number or not session_otp:
        messages.error(request, 'Please enter your phone number first.')
        return redirect('phone_login')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            user_otp = int(form.cleaned_data['otp'])
            
            if str(user_otp) == str(session_otp):
                try:
                    profile = UserProfile.objects.get(phone_number=phone_number)
                    user = profile.user
                except UserProfile.DoesNotExist:
                    username = f'user_{phone_number}'
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f'user_{phone_number}_{counter}'
                        counter += 1
                    
                    user = User.objects.create_user(username=username)
                    user.set_unusable_password()

                    user.save()
                    
                    user.profile.phone_number = phone_number
                    user.profile.save()
                
                login(request, user)
                messages.success(request, 'Welcome! You are logged in successfully.')
                
                del request.session['phone_number']
                del request.session['otp']
                
                return redirect('home') # Yahan se 302 Redirect hona chahiye
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                # Galat OTP par wahi page dobara dikhega (200 OK)
    
    form = OTPForm()
    return render(request, 'accounts/verify_otp.html', {'form': form})


# --- Baaki ke sabhi views waise hi rahenge ---
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    addresses = Address.objects.filter(user=request.user)
    address_form = AddressForm()
    context = {
        'orders': orders,
        'addresses': addresses,
        'address_form': address_form,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('profile')

# ... (edit_address, delete_address, etc. sabhi views yahan rahenge)
@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/edit_address.html', {'form': form, 'address_id': address_id})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        if request.user.addresses.count() <= 1:
            messages.error(request, 'You cannot delete your only address.')
        elif address.is_default:
            messages.error(request, 'You cannot delete your default address.')
        else:
            address.delete()
            messages.success(request, 'Address deleted successfully!')
    return redirect('profile')

@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f'Address has been set as default.')
    return redirect('profile')

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items', 'items__product'), order_id=order_id, user=request.user)
    return render(request, 'accounts/order_detail.html', {'order': order})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=request.user.profile)
    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def delete_profile_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    return render(request, 'accounts/delete_profile_confirm.html')