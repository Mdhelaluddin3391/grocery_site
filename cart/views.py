# cart/views.py (FINAL UPDATED CODE with Custom Customer Auth)

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from django.db import transaction
from accounts.models import Address, Customer
from accounts.forms import AddressForm
from django.contrib import messages
from store.views import get_main_categories
from accounts.views import customer_login_required # Custom decorator

# --- HELPER FUNCTION ---
def get_current_customer(request):
    """Session ID se Customer object retrieve karein."""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        # customer_login_required decorator ise sambhalega
        return None 
    return get_object_or_404(Customer, id=customer_id)
# -----------------------


@customer_login_required
def add_to_cart(request, product_id):
    customer = get_current_customer(request)
    product = get_object_or_404(Product, id=product_id)
    # Cart ab Customer se link hogi
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if not created:
        if product.stock > cart_item.quantity:
            cart_item.quantity += 1
        else:
            if is_ajax:
                return JsonResponse({'error': 'Stock limit reached'}, status=400)
            messages.error(request, f"Sorry, you cannot add more of '{product.name}'. Stock limit reached.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    cart_item.save()

    if is_ajax:
        return JsonResponse({
            'cart_item_count': cart.get_total_items(),
            'product_name': product.name
        })

    messages.success(request, f"'{product.name}' has been added to your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@customer_login_required
def view_cart(request):
    customer = get_current_customer(request)
    cart, created = Cart.objects.get_or_create(customer=customer)
    context = {
        'cart': cart,
        'main_categories': get_main_categories(),
    }
    return render(request, 'cart/cart_detail.html', context)

@customer_login_required
def remove_from_cart(request, item_id):
    # Customer cart item delete kar raha hai
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=get_current_customer(request))
    item_id_for_json = cart_item.id
    cart = cart_item.cart
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_data = cart.get_data_for_json()
        cart_data.update({'item_removed': True, 'item_id': item_id_for_json})
        return JsonResponse(cart_data)

    return redirect('view_cart')

@customer_login_required
def increment_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=get_current_customer(request))
    if cart_item.product.stock > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        return JsonResponse({'error': 'Stock limit reached'}, status=400)
    
    cart_data = cart_item.cart.get_data_for_json()
    cart_data.update({
        'item_quantity': cart_item.quantity,
        'item_subtotal': cart_item.get_subtotal(),
    })
    return JsonResponse(cart_data)

@customer_login_required
def decrement_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=get_current_customer(request))
    cart = cart_item.cart
    item_removed = False
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        item_removed = True

    cart_data = cart.get_data_for_json()
    cart_data.update({
        'item_quantity': 0 if item_removed else cart_item.quantity,
        'item_subtotal': 0 if item_removed else cart_item.get_subtotal(),
        'item_removed': item_removed,
        'item_id': item_id,
    })
    return JsonResponse(cart_data)

@customer_login_required
def checkout(request):
    customer = get_current_customer(request)
    cart = get_object_or_404(Cart, customer=customer)
    if not cart.items.all().exists():
        return redirect('view_cart')

    # Addresses ab customer se linked hain
    addresses = Address.objects.filter(customer=customer).order_by('-is_default')
    address_form = AddressForm()
    
    if request.method == 'POST':
        selected_address = None
        address_choice = request.POST.get('address_choice')

        if address_choice == 'existing' and request.POST.get('selected_address'):
            address_id = request.POST.get('selected_address')
            selected_address = get_object_or_404(Address, id=address_id, customer=customer)
        
        elif address_choice == 'new':
            form = AddressForm(request.POST)
            if form.is_valid():
                selected_address = form.save(commit=False)
                selected_address.customer = customer # Customer set karein
                
                lat = request.POST.get('latitude')
                lng = request.POST.get('longitude')
                
                selected_address.latitude = lat if lat else None
                selected_address.longitude = lng if lng else None

                selected_address.save()
            else:
                return render(request, 'cart/checkout.html', { 'cart': cart, 'addresses': addresses, 'address_form': form, 'error': 'Please correct the address errors.' })

        if not selected_address:
            return render(request, 'cart/checkout.html', { 'cart': cart, 'addresses': addresses, 'address_form': address_form, 'error': 'Please select or add a shipping address.' })

        payment_method = request.POST.get('payment_method')
        if payment_method == 'COD':
            with transaction.atomic():
                shipping_address_str = (
                    f"{selected_address.address_line_1}, "
                    f"{selected_address.address_line_2 + ', ' if selected_address.address_line_2 else ''}"
                    f"{selected_address.city}, {selected_address.state} - {selected_address.pincode}"
                )
                
                order = Order.objects.create(
                    customer=customer, # Customer set karein
                    shipping_address=shipping_address_str,
                    total_amount=cart.get_grand_total(),
                    payment_method='COD',
                    payment_status=False
                )

                for item in cart.items.all():
                    product = item.product
                    if product.stock < item.quantity:
                        messages.error(request, f"Sorry, '{product.name}' is now out of stock.")
                        return redirect('view_cart')
                    
                    OrderItem.objects.create(
                        order=order, 
                        product=product, 
                        quantity=item.quantity, 
                        price=product.price
                    )
                    product.stock -= item.quantity
                    product.save()

                cart.items.all().delete()
            return redirect('order_successful', order_id=order.order_id)
        
        elif payment_method == 'UPI':
            # Ab yahan customer_id session mein hai
            request.session['shipping_address_id'] = selected_address.id 
            return redirect('process_payment')

        else:
            return render(request, 'cart/checkout.html', { 'cart': cart, 'addresses': addresses, 'address_form': address_form, 'error': 'Please select a valid payment method.' })

    return render(request, 'cart/checkout.html', { 'cart': cart, 'addresses': addresses, 'address_form': address_form })

@customer_login_required
def process_payment(request):
    address_id = request.session.get('shipping_address_id')
    if not address_id:
        return redirect('checkout')

    # Address ab customer se linked hai
    address = get_object_or_404(Address, id=address_id, customer=get_current_customer(request))
    cart = get_object_or_404(Cart, customer=get_current_customer(request))
    
    context = {
        'address': address,
        'cart': cart
    }
    return render(request, 'cart/process_payment.html', context)

@customer_login_required
def order_successful(request, order_id):
    # Order ab customer se linked hai
    order = get_object_or_404(Order, order_id=order_id, customer=get_current_customer(request))
    context = {
        'order': order,
        'main_categories': get_main_categories(),
    }
    return render(request, 'cart/order_successful.html', context)