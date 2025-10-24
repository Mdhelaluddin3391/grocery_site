# dashboard/views.py (UPDATED)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator

from cart.models import Order
from django.contrib import messages

def is_staff(user):
    return user.is_staff

# --- DECORATORS IN ALL VIEWS ARE NOW UPDATED ---

@login_required
@user_passes_test(is_staff, login_url='/admin/login/')
def dashboard_home(request):
    # KPI Calculations
    total_revenue = Order.objects.filter(status='Delivered').aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders_count = Order.objects.count()
    pending_orders_count = Order.objects.filter(status='Pending').count()
    total_customers_count = User.objects.filter(is_staff=False).count()

    # Recent Orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]

    context = {
        'total_revenue': total_revenue,
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'total_customers_count': total_customers_count,
        'orders': recent_orders,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
@user_passes_test(is_staff, login_url='/admin/login/')
def order_list(request):
    """Displays a paginated and filterable list of all orders."""
    orders_queryset = Order.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status', 'all')
    if status_filter and status_filter != 'all':
        orders_queryset = orders_queryset.filter(status=status_filter)

    paginator = Paginator(orders_queryset, 15)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    context = {
        'orders': orders_page,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
    }
    return render(request, 'dashboard/order_list.html', context)

@login_required
@user_passes_test(is_staff, login_url='/admin/login/')
def dashboard_order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_id=order_id)
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES 
    }
    return render(request, 'dashboard/order_detail.html', context)

@login_required
@user_passes_test(is_staff, login_url='/admin/login/')
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id)
        new_status = request.POST.get('status')
        valid_statuses = [status[0] for status in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f"Order {order.order_id} status has been updated to '{new_status}'.")
        else:
            messages.error(request, "Invalid status selected.")
    return redirect('dashboard_order_detail', order_id=order_id)

@login_required
@user_passes_test(is_staff, login_url='/admin/login/')
def customer_list(request):
    """Displays a list of all non-staff customers with their order counts."""
    customers = User.objects.filter(is_staff=False).annotate(
        order_count=Count('orders')
    ).order_by('-date_joined')
    
    paginator = Paginator(customers, 15)
    page_number = request.GET.get('page')
    customers_page = paginator.get_page(page_number)
    
    context = {
        'customers': customers_page,
    }
    return render(request, 'dashboard/customer_list.html', context)