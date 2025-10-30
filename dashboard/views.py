# dashboard/views.py
import csv
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from cart.models import Order, OrderItem
from users.models import CustomUser
from django.db.models import Sum, Count, Avg
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models.functions import TruncHour, TruncMonth

def staff_check(user):
    return user.is_authenticated and user.is_staff

def staff_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')
    return render(request, 'dashboard/login.html')

def staff_logout_view(request):
    logout(request)
    return redirect('staff_login')

@user_passes_test(staff_check, login_url='staff_login')
def dashboard_home_view(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    todays_orders_count = Order.objects.filter(created_at__date=today).count()
    pending_orders_count = Order.objects.filter(status='Pending').count()
    total_revenue_agg = Order.objects.filter(payment_status=True).aggregate(total=Sum('total_amount'))
    total_revenue = total_revenue_agg['total'] or 0.00
    total_customers_count = CustomUser.objects.filter(is_customer=True).count()
    new_customers_this_month = CustomUser.objects.filter(is_customer=True, date_joined__gte=start_of_month).count()
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    context = {
        'todays_orders': todays_orders_count,
        'pending_orders': pending_orders_count,
        'total_revenue': total_revenue,
        'total_customers': total_customers_count,
        'new_customers_this_month': new_customers_this_month,
        'recent_orders_page': recent_orders,
    }
    return render(request, 'dashboard/home.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def live_orders_view(request):
    order_list = Order.objects.select_related('user', 'picking_job__picker').all().order_by('-created_at')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        order_list = order_list.filter(created_at__date__range=[start_date, end_date])
    status_filter = request.GET.get('status')
    valid_statuses = ['Pending', 'Processing', 'Packed', 'Dispatched', 'Delivered', 'Cancelled']
    if status_filter and status_filter in valid_statuses:
        order_list = order_list.filter(status=status_filter)
    else:
        status_filter = 'All'
    query = request.GET.get('q')
    if query:
        order_list = order_list.filter(order_id__icontains=query)
    paginator = Paginator(order_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    stats = {
        'pending': Order.objects.filter(status='Pending').count(),
        'processing': Order.objects.filter(status='Processing').count(),
        'packed': Order.objects.filter(status='Packed').count(),
        'dispatched': Order.objects.filter(status='Dispatched').count(),
    }
    context = {
        'orders_page': page_obj, 'stats': stats,
        'search_query': query or "", 'active_status': status_filter,
        'start_date': start_date_str, 'end_date': end_date_str,
    }
    return render(request, 'dashboard/live_orders.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.order_id} status has been updated to '{new_status}'.")
            return redirect('order_detail', order_id=order.order_id)
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'dashboard/order_detail.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def delivery_map_view(request):
    return render(request, 'dashboard/delivery_map.html')

@user_passes_test(staff_check, login_url='staff_login')
def customers_view(request):
    customer_list = CustomUser.objects.filter(is_customer=True).order_by('-date_joined')
    paginator = Paginator(customer_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard/customers.html', {'customers_page': page_obj})

@user_passes_test(staff_check, login_url='staff_login')
def finance_view(request):
    total_revenue_agg = Order.objects.aggregate(total=Sum('total_amount'))
    total_revenue = total_revenue_agg['total'] or 0.00
    total_orders = Order.objects.count()
    average_order_value_agg = Order.objects.aggregate(avg=Avg('total_amount'))
    average_order_value = average_order_value_agg['avg'] or 0.00
    context = {'total_revenue': total_revenue, 'total_orders': total_orders, 'average_order_value': average_order_value}
    return render(request, 'dashboard/finance.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def analytics_view(request):
    return render(request, 'dashboard/analytics.html')

@user_passes_test(staff_check, login_url='staff_login')
def update_order_status_from_list(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id)
        next_status = request.POST.get('next_status')
        valid_transitions = {'Processing': 'Packed', 'Packed': 'Dispatched'}
        if order.status in valid_transitions and next_status == valid_transitions[order.status]:
            order.status = next_status
            order.save()
            messages.success(request, f"Order #{order_id} moved to '{next_status}'.")
        else:
            messages.error(request, "Invalid status transition.")
    return redirect('live_orders')

@user_passes_test(staff_check, login_url='staff_login')
def cancel_order_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if order.status in ['Pending', 'Processing', 'Packed']:
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #{order_id} has been cancelled and items restocked.")
    else:
        messages.error(request, f"Cannot cancel order. It is already {order.status}.")
    return redirect('live_orders')

def export_orders_csv(request):
    order_list = Order.objects.select_related('user', 'picking_job__picker').all().order_by('-created_at')
    # Aapke diye gaye code se filtering logic yahan add hoga
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Picker', 'Status', 'Total', 'Date'])
    for order in order_list:
        picker_name = order.picking_job.picker.name if hasattr(order, 'picking_job') and order.picking_job.picker else 'N/A'
        writer.writerow([order.order_id, order.user.name if order.user else 'N/A', picker_name, order.status, order.total_amount, order.created_at.strftime('%Y-%m-%d %H:%M')])
    return response

@user_passes_test(staff_check, login_url='staff_login')
def orders_per_hour_api(request):
    last_24_hours = timezone.now() - timedelta(hours=24)
    orders_by_hour = Order.objects.filter(created_at__gte=last_24_hours).annotate(hour=TruncHour('created_at')).values('hour').annotate(count=Count('id')).order_by('hour')
    labels = [h['hour'].strftime('%H:%M') for h in orders_by_hour]
    data = [h['count'] for h in orders_by_hour]
    return JsonResponse({'labels': labels, 'data': data})

@user_passes_test(staff_check, login_url='staff_login')
def top_selling_items_api(request):
    top_items = OrderItem.objects.values('product__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5]
    labels = [item['product__name'] for item in top_items]
    data = [item['total_sold'] for item in top_items]
    return JsonResponse({'labels': labels, 'data': data})

@user_passes_test(staff_check, login_url='staff_login')
def monthly_revenue_api(request):
    revenue_by_month = Order.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total_revenue=Sum('total_amount')).order_by('month')
    labels = [r['month'].strftime('%b %Y') for r in revenue_by_month]
    data = [float(r['total_revenue']) for r in revenue_by_month]
    return JsonResponse({'labels': labels, 'data': data})


@user_passes_test(staff_check, login_url='staff_login')
def packed_orders_view(request):
    """
    Manager ko sabhi packed orders dikhata hai, rider assign karne ke option ke saath.
    """
    packed_orders = Order.objects.filter(status='Packed').order_by('created_at')
    
    # Sabhi available riders (staff users) ko fetch karein
    available_riders = CustomUser.objects.filter(is_staff=True, is_superuser=False)

    context = {
        'packed_orders': packed_orders,
        'available_riders': available_riders,
    }
    return render(request, 'dashboard/packed_orders.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def cancel_order_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    
    # Sirf un-dispatched orders hi cancel ho sakte hain
    if order.status in ['Pending', 'Processing', 'Packed']:
        # Stock wapas add karein
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
            
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order #{order_id} has been successfully cancelled and items are restocked.")
    else:
        messages.error(request, f"Cannot cancel order. It has already been {order.status}.")
        
    return redirect('live_orders')