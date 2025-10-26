from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from cart.models import Order
from django.contrib.auth.decorators import login_required
from .models import CustomerProfile

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # create user as customer explicitly
            user = form.save(commit=False)
            user.is_customer = True  # ensure this user is a customer
            user.is_staff = False
            user.save()
            # signal will create CustomerProfile because is_customer=True
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=phone_number, password=password)
            # Use is_customer check for webapp customer login
            if user is not None and getattr(user, 'is_customer', False):
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid customer credentials.")
    form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    # Only customers can view the customer profile page
    if not getattr(request.user, 'is_customer', False):
        return redirect('home')
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    addresses = request.user.addresses.all()
    context = {'profile': profile, 'orders': orders, 'addresses': addresses}
    return render(request, 'users/profile.html', context)
