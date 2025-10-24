from django.shortcuts import render, redirect, get_object_or_404
from cart.models import Order
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

# Yeh function check karega ki user staff hai ya nahi
def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def dashboard_home(request):
    # ... (yeh function jaisa hai waisa hi rahega) ...
    orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'orders': orders
    }
    return render(request, 'dashboard/home.html', context)

# --- YEH DO NAYE VIEWS JODEIN ---

@login_required
@user_passes_test(is_staff)
def dashboard_order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_id=order_id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES 
    }
    return render(request, 'dashboard/order_detail.html', context)

@login_required
@user_passes_test(is_staff)
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id)
        new_status = request.POST.get('status')
        
        # Check karein ki naya status valid hai
        valid_statuses = [status[0] for status in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f"Order {order.order_id} status has been updated to '{new_status}'.")
        else:
            messages.error(request, "Invalid status selected.")
            
    return redirect('dashboard_order_detail', order_id=order_id)