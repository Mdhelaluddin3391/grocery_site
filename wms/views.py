# wms/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Inventory
from store.models import Product  # Product model ko store se import karein
from .forms import StockMovementForm

# Helper function to check if user is staff
def staff_check(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(staff_check, login_url='staff_login')
def inventory_list_view(request):
    inventory_items = Inventory.objects.select_related('product').all().order_by('product__name')
    context = {'inventory_items': inventory_items}
    return render(request, 'wms/inventory_list.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def adjust_stock_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.product = product
            movement.user = request.user
            movement.save()
            messages.success(request, f"Stock for '{product.name}' has been updated.")
            return redirect('inventory_list')
    else:
        form = StockMovementForm()

    # Product ke liye inventory get ya create karein
    inventory, _ = Inventory.objects.get_or_create(product=product)

    context = {
        'form': form,
        'product': product,
        'inventory': inventory
    }
    return render(request, 'wms/adjust_stock.html', context)