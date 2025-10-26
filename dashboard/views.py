from django.shortcuts import render

# Create your views here.
# dashboard/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from users.forms import CustomAuthenticationForm
from django.contrib.auth.decorators import staff_member_required

def staff_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=phone_number, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('dashboard_home')
            else:
                messages.error(request, "Only staff members can log in here.")
    form = CustomAuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

@staff_member_required
def dashboard_home_view(request):
    return render(request, 'dashboard/home.html')

def staff_logout_view(request):
    logout(request)
    return redirect('staff_login')