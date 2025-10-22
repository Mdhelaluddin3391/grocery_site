# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
# AddressForm ko bhi import karna hai
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AddressForm
from django.contrib.auth.decorators import login_required
from cart.models import Order
from .models import Address # Address model ko import karein

# --- AUTHENTICATION VIEWS (YEH MISSING THE) ---
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


# --- PROFILE AND ADDRESS VIEWS ---
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
            return redirect('profile')
    return redirect('profile')

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    # Edit logic yahan aayega
    return redirect('profile')

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return redirect('profile')