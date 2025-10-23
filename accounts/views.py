# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AddressForm, UserUpdateForm, UserProfileUpdateForm
from django.contrib.auth.decorators import login_required
from cart.models import Order
from .models import Address
from django.contrib import messages
# JSON aur render_to_string ki ab zaroorat nahi
# from django.http import JsonResponse
# from django.template.loader import render_to_string

# --- AUTHENTICATION VIEWS (No Changes) ---
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


# --- PROFILE AND ADDRESS VIEWS (Reverted to simple version) ---
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
    return redirect('profile') # Hamesha profile page par redirect karega

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
    
    if request.user.addresses.count() <= 1:
        messages.error(request, 'You cannot delete your only address. Please edit it instead.')
        return redirect('profile')

    if address.is_default:
        messages.error(request, 'You cannot delete your default address. Please set another address as default first.')
        return redirect('profile')

    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
    
    return redirect('profile') # Hamesha profile page par redirect karega

# --- Other views (No Changes) ---
@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items', 'items__product'), 
        order_id=order_id, 
        user=request.user
    )
    context = {'order': order}
    return render(request, 'accounts/order_detail.html', context)

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