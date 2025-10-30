# riders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse

from .models import RiderProfile
from cart.models import Order
from users.models import CustomUser

def staff_check(user):
    return user.is_authenticated and user.is_staff

# --- MANAGER KA DASHBOARD ---
@user_passes_test(staff_check, login_url='staff_login')
def rider_dashboard_view(request):
    """
    Riders ka manager dashboard jahan unki list aur status dikhega.
    """
    riders = RiderProfile.objects.select_related('user').all()
    context = {'riders': riders}
    return render(request, 'riders/rider_dashboard.html', context)

# --- RIDER KA PERSONAL APP DASHBOARD ---
@user_passes_test(staff_check, login_url='staff_login')
def rider_app_dashboard_view(request):
    """
    Rider ko uske assigned delivery jobs dikhata hai.
    """
    assigned_orders = Order.objects.filter(
        status='Dispatched',
        rider=request.user
    ).order_by('created_at')
    
    context = {'assigned_orders': assigned_orders}
    return render(request, 'riders/app/rider_app_dashboard.html', context)

# --- RIDER KO ORDER ASSIGN KARNE KE LIYE VIEW ---
@user_passes_test(staff_check, login_url='staff_login')
def assign_rider_view(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id)
        rider_id = request.POST.get('rider_id')

        if not rider_id:
            messages.error(request, "Please select a rider.")
            return redirect('packed_orders')

        try:
            rider_user = CustomUser.objects.get(id=rider_id, is_staff=True)
            order.rider = rider_user
            order.status = 'Dispatched'
            order.save()

            if hasattr(rider_user, 'riderprofile'):
                rider_user.riderprofile.current_status = 'ON_DELIVERY'
                rider_user.riderprofile.save()

            messages.success(request, f"Order #{order.order_id} has been dispatched with {rider_user.name}.")
        except CustomUser.DoesNotExist:
            messages.error(request, "The selected rider does not exist.")
    
    return redirect('packed_orders')

# --- ORDER DELIVER MARK KARNE KE LIYE VIEW ---
@user_passes_test(staff_check, login_url='staff_login')
def mark_as_delivered_view(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id, rider=request.user)
        order.status = 'Delivered'
        order.payment_status = True # Maan rahe hain ki COD mil gaya
        order.save()

        if hasattr(request.user, 'riderprofile'):
            request.user.riderprofile.current_status = 'AVAILABLE'
            request.user.riderprofile.save()

        messages.success(request, f"Order #{order_id} has been marked as Delivered.")
    return redirect('rider_app_dashboard')

# --- LIVE MAP KE LIYE API ---
@user_passes_test(staff_check, login_url='staff_login')
def get_rider_locations_api(request):
    """
    Active riders ki live location JSON format mein bhejta hai.
    """
    active_riders = RiderProfile.objects.exclude(current_status='OFFLINE').select_related('user')
    
    locations = []
    for rider in active_riders:
        if rider.last_known_latitude and rider.last_known_longitude:
            locations.append({
                'rider_id': rider.id,
                'name': rider.user.name or rider.user.email,
                'lat': float(rider.last_known_latitude),
                'lng': float(rider.last_known_longitude),
                'status': rider.get_current_status_display(),
            })
            
    return JsonResponse({'locations': locations})