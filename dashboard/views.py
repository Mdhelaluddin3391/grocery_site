# dashboard/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test

# ✅ Only allow staff to access dashboard pages
def staff_check(user):
    return user.is_authenticated and user.is_staff

# --- LOGIN VIA GOOGLE ---
def staff_login_view(request):
    """
    Staff will not log in manually here.
    They will click 'Continue with Google' which triggers allauth flow.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')

    # Show a simple page with 'Continue with Google' button
    return render(request, 'dashboard/login.html')


# --- DASHBOARD HOME ---
@login_required
@user_passes_test(staff_check, login_url='/accounts/google/login/')
def dashboard_home_view(request):
    """
    Main dashboard for staff (only after Google login).
    """
    return render(request, 'dashboard/home.html')


# --- LOGOUT STAFF ---
@login_required
def staff_logout_view(request):
    logout(request)
    return redirect('staff_login')
