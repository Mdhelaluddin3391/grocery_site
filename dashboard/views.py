# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import timedelta
from cart.models import Order
from users.models import CustomUser
from django.db.models import Sum, Count
from django.core.paginator import Paginator

def staff_check(user):
    return user.is_authenticated and user.is_staff

def staff_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')
    return render(request, 'dashboard/login.html')

@user_passes_test(staff_check, login_url='/accounts/google/login/')
def dashboard_home_view(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # Statistics Calculation
    todays_orders = Order.objects.filter(created_at__date=today).count()
    pending_orders = Order.objects.filter(status='Pending').count()
    total_revenue = Order.objects.filter(payment_status=True).aggregate(total=Sum('total_amount'))['total'] or 0.00
    monthly_revenue = Order.objects.filter(created_at__gte=start_of_month, payment_status=True).aggregate(total=Sum('total_amount'))['total'] or 0.00
    total_customers = CustomUser.objects.filter(is_customer=True).count()
    new_customers_this_month = CustomUser.objects.filter(is_customer=True, date_joined__gte=start_of_month).count()

    # Recent Orders with Pagination
    order_list = Order.objects.all().order_by('-created_at')
    paginator = Paginator(order_list, 10) # Har page par 10 order
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'todays_orders': todays_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
        'recent_orders_page': page_obj, # Updated context variable
    }
    return render(request, 'dashboard/home.html', context)



@user_passes_test(staff_check, login_url='/accounts/google/login/')
def live_orders_view(request):
    """
    Live orders dashboard dikhata hai.
    """
    all_orders = Order.objects.all().order_by('-created_at')
    
    # Order stats calculate karein
    today = timezone.now().date()
    stats = {
        'total_shipped_today': Order.objects.filter(created_at__date=today, status__in=['Shipped', 'Delivered']).count(),
        'pack_in_progress': Order.objects.filter(status='Processing').count(),
        'packed': Order.objects.filter(status='Shipped').count(), # Assuming 'Packed' is same as 'Shipped' for now
        'dispatched': Order.objects.filter(status='Shipped').count(), # Assuming 'Dispatched' is same as 'Shipped'
        'delivered': Order.objects.filter(status='Delivered').count(),
    }

    # Search functionality
    query = request.GET.get('q')
    if query:
        all_orders = all_orders.filter(order_id__icontains=query)

    paginator = Paginator(all_orders, 20) # Ek page par 20 orders
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders_page': page_obj,
        'stats': stats,
        'search_query': query or "",
    }
    return render(request, 'dashboard/live_orders.html', context)

@user_passes_test(staff_check, login_url='/accounts/google/login/')
def order_detail_view(request, order_id):
    """
    Ek specific order ki poori details dikhata hai.
    """
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'dashboard/order_detail.html', context)

@user_passes_test(staff_check, login_url='/accounts/google/login/')
def wms_view(request):
    """
    Warehouse Management System (WMS) page ko render karta hai.
    """
    return render(request, 'dashboard/wms.html')

def staff_logout_view(request):
    logout(request)
    return redirect('staff_login')