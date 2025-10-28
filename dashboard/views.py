# dashboard/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
from cart.models import Order
from users.models import CustomUser
from django.db.models import Sum

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
@user_passes_test(staff_check, login_url='/accounts/google/login/')
def dashboard_home_view(request):
    """
    Main dashboard for staff (only after Google login).
    """
    # Calculate statistics
    today = timezone.now().date()
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

    todays_orders = Order.objects.filter(created_at__range=(start_of_day, end_of_day)).count()
    pending_orders = Order.objects.filter(status='Pending').count()
    total_revenue = Order.objects.filter(payment_status=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
    total_customers = CustomUser.objects.filter(is_customer=True).count()
    
    # Fetch recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]

    context = {
        'todays_orders': todays_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/home.html', context)


# --- LOGOUT STAFF ---
@login_required
def staff_logout_view(request):
    logout(request)
    return redirect('staff_login')