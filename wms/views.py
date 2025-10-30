# wms/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Inventory, Product, PurchaseOrder, PurchaseOrderItem, GoodsReceivedNote, StockMovement, Vendor, Location
from .forms import PurchaseOrderForm, GRNForm, StockMovementForm
from django.db import transaction

def staff_check(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(staff_check, login_url='staff_login')
def inventory_list_view(request):
    inventory_items = Inventory.objects.select_related('product', 'location').all().order_by('product__name')
    context = {'inventory_items': inventory_items}
    return render(request, 'wms/inventory_list.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def purchase_order_list(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Purchase order created successfully.")
            return redirect('purchase_order_list')
    else:
        form = PurchaseOrderForm()

    purchase_orders = PurchaseOrder.objects.all().order_by('-created_at')
    context = {
        'form': form,
        'purchase_orders': purchase_orders,
    }
    return render(request, 'wms/purchase_order_list.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def purchase_order_detail(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)
    context = {'po': po}
    return render(request, 'wms/purchase_order_detail.html', context)

@user_passes_test(staff_check, login_url='staff_login')
@transaction.atomic
def receive_goods(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)
    if request.method == 'POST':
        form = GRNForm(request.POST)
        if form.is_valid():
            grn = form.save(commit=False)
            grn.purchase_order = po
            grn.grn_number = f"GRN-{po.po_number}"
            grn.save()

            for item in po.items.all():
                received_qty = int(request.POST.get(f'quantity_{item.product.id}', 0))
                location_id = request.POST.get(f'location_{item.product.id}')
                location = get_object_or_404(Location, id=location_id)

                if received_qty > 0:
                    # Update Inventory
                    inventory_item, created = Inventory.objects.get_or_create(
                        product=item.product,
                        location=location,
                        defaults={'quantity': 0}
                    )
                    inventory_item.quantity += received_qty
                    inventory_item.save()

                    # Create Stock Movement record
                    StockMovement.objects.create(
                        product=item.product,
                        movement_type='IN',
                        quantity=received_qty,
                        remarks=f"Received against GRN {grn.grn_number}",
                        user=request.user,
                        grn=grn
                    )

            po.status = 'Completed'
            po.save()
            messages.success(request, "Goods received and inventory updated.")
            return redirect('purchase_order_list')
    else:
        form = GRNForm()

    locations = Location.objects.all()
    context = {
        'form': form,
        'po': po,
        'locations': locations,
    }
    return render(request, 'wms/receive_goods.html', context)