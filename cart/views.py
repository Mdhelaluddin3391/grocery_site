# cart/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from django.contrib.auth.decorators import login_required
from store.views import get_main_categories
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from django.contrib.auth.decorators import login_required
from store.views import get_main_categories
from django.db import transaction
from accounts.models import Address
from accounts.forms import AddressForm
from django.contrib import messages # messages ko import karein

# ... add_to_cart, view_cart, remove_from_cart views waise hi rahenge ...

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Stock check karein
    if created:
        # Agar item pehli baar add ho raha hai
        if product.stock < 1:
            cart_item.delete()
            messages.error(request, f"Sorry, '{product.name}' is out of stock.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Out of stock'}, status=400)
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        # Agar item pehle se cart mein hai
        if product.stock <= cart_item.quantity:
            messages.error(request, f"Sorry, you cannot add more of '{product.name}'. Stock limit reached.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Stock limit reached'}, status=400)
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        cart_item.quantity += 1
    
    cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_item_count': cart.get_total_items()})
    
    messages.success(request, f"'{product.name}' has been added to your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))



@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart': cart,
        'main_categories': get_main_categories(),
    }
    return render(request, 'cart/cart_detail.html', context)

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = cart_item.cart # Cart ko pehle hi le lo
    item_id_str = str(cart_item.id) # ID ko string mein save kar lo
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Agar yeh ek AJAX request hai, toh JSON response bhejein
        cart_data = cart.get_data_for_json()
        cart_data['item_removed'] = True
        cart_data['item_id'] = item_id_str
        return JsonResponse(cart_data)
    
    # Normal request ke liye, redirect karein
    return redirect('view_cart')

# --- UPDATED VIEWS ---

def get_cart_data(cart):
    """Helper function to create a dictionary of cart data."""
    return {
        'cart_subtotal': cart.get_subtotal(),
        'cart_grand_total': cart.get_grand_total(),
        'cart_item_count': sum(item.quantity for item in cart.items.all()),
    }

@login_required
def increment_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    
    # Model se fresh data get karo
    cart_data = cart_item.cart.get_data_for_json()
    
    # Is item ka specific data bhi add karo
    cart_data.update({
        'item_quantity': cart_item.quantity,
        'item_subtotal': cart_item.get_subtotal(),
    })
    return JsonResponse(cart_data)

@login_required
def decrement_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = cart_item.cart # Cart ko pehle hi le lo
    item_removed = False
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        item_removed = True

    # Model se fresh data get karo
    cart_data = cart.get_data_for_json()

    # Is item ka specific data bhi add karo
    cart_data.update({
        'item_quantity': 0 if item_removed else cart_item.quantity,
        'item_subtotal': 0 if item_removed else cart_item.get_subtotal(),
        'item_removed': item_removed,
        'item_id': item_id
    })
    return JsonResponse(cart_data)

# --- CHECKOUT VIEW ---

# cart/views.py


# ... (other views remain the same) ...

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.all().exists():
        return redirect('view_cart')

    addresses = Address.objects.filter(user=request.user)
    address_form = AddressForm()
    
    if request.method == 'POST':
        selected_address = None
        
        # Step 1: Address select ya create karein
        if request.POST.get('selected_address'):
            address_id = request.POST.get('selected_address')
            selected_address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            form = AddressForm(request.POST)
            if form.is_valid():
                selected_address = form.save(commit=False)
                selected_address.user = request.user
                selected_address.latitude = request.POST.get('latitude')
                selected_address.longitude = request.POST.get('longitude')
                selected_address.save()
            else:
                return render(request, 'cart/checkout.html', { 'cart': cart, 'addresses': addresses, 'address_form': form, 'error': 'Please correct the address errors.' })

        if not selected_address:
            return render(request, 'cart/checkout.html', { 'cart': cart, 'addresses': addresses, 'address_form': address_form, 'error': 'Please select or add a shipping address.' })

        # Step 2: Payment method ke hisaab se action lein
        payment_method = request.POST.get('payment_method')

        if payment_method == 'COD':
            with transaction.atomic():
                shipping_address_str = f"{selected_address.address_line_1}, {selected_address.city}, {selected_address.pincode}"
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address_str,
                    total_amount=cart.get_grand_total(),
                    payment_method='COD',
                    payment_status=False # COD mein payment pending rehta hai
                )
                for item in cart.items.all():
                    OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
                cart.items.all().delete()
            return redirect('order_successful', order_id=order.order_id)

        elif payment_method == 'UPI':
            # Abhi ke liye, hum order create nahi karenge. Sirf payment page par bhejenge.
            # Hum address aur cart ki details ko session mein save kar sakte hain
            request.session['shipping_address_id'] = selected_address.id
            # Asli project mein yahan payment gateway ka code aayega
            return redirect('process_payment') # Naya URL

        else:
            return render(request, 'cart/checkout.html', { 'cart': cart, 'addresses': addresses, 'address_form': address_form, 'error': 'Please select a payment method.' })

    return render(request, 'cart/checkout.html', { 'cart': cart, 'addresses': addresses, 'address_form': address_form })

@login_required
def process_payment(request):
    # Yeh ek placeholder view hai UPI payment ke liye
    address_id = request.session.get('shipping_address_id')
    if not address_id:
        return redirect('checkout')

    address = get_object_or_404(Address, id=address_id)
    cart = get_object_or_404(Cart, user=request.user)
    
    context = {
        'address': address,
        'cart': cart
    }
    return render(request, 'cart/process_payment.html', context)

@login_required
def order_successful(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    context = {
        'order': order,
        'main_categories': get_main_categories(),
    }
    return render(request, 'cart/order_successful.html', context)