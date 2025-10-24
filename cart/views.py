# cart/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from django.contrib.auth.decorators import login_required
from store.views import get_main_categories
from django.db import transaction
from accounts.models import Address
from accounts.forms import AddressForm
from django.contrib import messages

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if product.stock > cart_item.quantity:
            cart_item.quantity += 1
        else:
            messages.error(request, f"Sorry, you cannot add more of '{product.name}'. Stock limit reached.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    cart_item.save()
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
    cart_item.delete()
    return redirect('view_cart')

@login_required
def increment_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if cart_item.product.stock > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        # Optionally, you can send a message back to the user
        return JsonResponse({'error': 'Stock limit reached'}, status=400)
        
    return JsonResponse({
        'item_quantity': cart_item.quantity,
        'item_subtotal': cart_item.get_subtotal(),
        'cart_subtotal': cart_item.cart.get_subtotal(),
        'cart_grand_total': cart_item.cart.get_grand_total(),
    })

@login_required
def decrement_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
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

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.all().exists():
        return redirect('view_cart')

    addresses = Address.objects.filter(user=request.user).order_by('-is_default')
    address_form = AddressForm()
    
    if request.method == 'POST':
        selected_address = None
        address_choice = request.POST.get('address_choice')

        if address_choice == 'existing' and request.POST.get('selected_address'):
            address_id = request.POST.get('selected_address')
            selected_address = get_object_or_404(Address, id=address_id, user=request.user)
        
        elif address_choice == 'new':
            form = AddressForm(request.POST)
            if form.is_valid():
                selected_address = form.save(commit=False)
                selected_address.user = request.user
                
                # --- ## ERROR FIX: Handle empty lat/lng values ---
                lat = request.POST.get('latitude')
                lng = request.POST.get('longitude')
                
                selected_address.latitude = lat if lat else None
                selected_address.longitude = lng if lng else None
                # -----------------------------------------------

                selected_address.save()
            else:
                # Agar form valid nahi hai, to error ke saath page dobara render karein
                return render(request, 'cart/checkout.html', { 
                    'cart': cart, 
                    'addresses': addresses, 
                    'address_form': form, 
                    'error': 'Please correct the address errors.' 
                })

        if not selected_address:
            # Agar koi bhi address select ya create nahi hua hai, to error dikhayein
            return render(request, 'cart/checkout.html', { 
                'cart': cart, 
                'addresses': addresses, 
                'address_form': address_form, 
                'error': 'Please select or add a shipping address.' 
            })

        payment_method = request.POST.get('payment_method')
        if payment_method == 'COD':
            with transaction.atomic():
                shipping_address_str = (
                    f"{selected_address.address_line_1}, "
                    f"{selected_address.address_line_2 + ', ' if selected_address.address_line_2 else ''}"
                    f"{selected_address.city}, {selected_address.state} - {selected_address.pincode}"
                )
                
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address_str,
                    total_amount=cart.get_grand_total(),
                    payment_method='COD',
                    payment_status=False
                )

                for item in cart.items.all():
                    # Order create karne se pehle stock check karein
                    product = item.product
                    if product.stock < item.quantity:
                        # Agar stock kam hai, to transaction rollback karein aur error dikhayein
                        messages.error(request, f"Sorry, '{product.name}' is now out of stock.")
                        return redirect('view_cart') # User ko cart page par wapas bhej dein
                    
                    OrderItem.objects.create(
                        order=order, 
                        product=product, 
                        quantity=item.quantity, 
                        price=product.price
                    )
                    # Stock kam karein
                    product.stock -= item.quantity
                    product.save()

                cart.items.all().delete()
            return redirect('order_successful', order_id=order.order_id)
        
        elif payment_method == 'UPI':
            # UPI logic yahan aayega
            return redirect('process_payment')

        else:
            return render(request, 'cart/checkout.html', { 
                'cart': cart, 
                'addresses': addresses, 
                'address_form': address_form, 
                'error': 'Please select a valid payment method.' 
            })

    # GET request ke liye
    return render(request, 'cart/checkout.html', { 
        'cart': cart, 
        'addresses': addresses, 
        'address_form': address_form 
    })

@login_required
def process_payment(request):
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