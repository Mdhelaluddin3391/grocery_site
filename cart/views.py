# cart/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from users.models import Address
from users.forms import AddressForm
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required # <-- YEH LINE ADD KAREIN

# --- HELPER FUNCTION ---
def get_cart(request):
    """Session ID se Cart object retrieve karein."""
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart
# -----------------------
@login_required(login_url='/users/login/') # <--- YEH DECORATOR ADD KAREIN
def add_to_cart(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if not created:
        if product.stock > cart_item.quantity:
            cart_item.quantity += 1
            cart_item.save()
        else:
            if is_ajax:
                return JsonResponse({'error': 'Stock limit reached'}, status=400)
            messages.error(request, f"Sorry, you cannot add more of '{product.name}'. Stock limit reached.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
       #  cart_item.save() # Ensure save even on creation if needed later
       pass

    if is_ajax:
        return JsonResponse({
            'cart_item_count': cart.get_total_items(),
            'product_name': product.name
        })

    messages.success(request, f"'{product.name}' has been added to your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required(login_url='/users/login/') # <--- YEH DECORATOR ADD KAREIN
def view_cart(request):
    cart = get_cart(request)
    context = {'cart': cart}
    return render(request, 'cart/cart_detail.html', context)

def remove_from_cart(request, item_id):
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item_id_for_json = cart_item.id
    product_name = cart_item.product.name # Get name before deleting
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_data = cart.get_data_for_json()
        cart_data.update({'item_removed': True, 'item_id': item_id_for_json})
        return JsonResponse(cart_data)

    messages.info(request, f"'{product_name}' removed from cart.")
    return redirect('view_cart')

def increment_cart_item(request, item_id):
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if cart_item.product.stock > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        return JsonResponse({'error': 'Stock limit reached'}, status=400)

    cart_data = cart.get_data_for_json()
    cart_data.update({
        'item_quantity': cart_item.quantity,
        'item_subtotal': cart_item.get_subtotal(),
    })
    return JsonResponse(cart_data)

def decrement_cart_item(request, item_id):
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item_removed = False
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        # Instead of deleting directly, maybe ask for confirmation or handle it in remove_from_cart logic
        # For now, let's keep the delete, but add a message.
        product_name = cart_item.product.name
        cart_item.delete()
        item_removed = True
        messages.info(request, f"'{product_name}' removed from cart.") # Add message for non-AJAX case


    cart_data = cart.get_data_for_json()
    cart_data.update({
        'item_quantity': 0 if item_removed else cart_item.quantity,
        'item_subtotal': 0 if item_removed else cart_item.get_subtotal(),
        'item_removed': item_removed,
        'item_id': item_id,
    })
    return JsonResponse(cart_data)

@login_required # Checkout ke liye login zaroori
def checkout(request):
    cart = get_cart(request)
    if not cart.items.all().exists():
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    addresses = request.user.addresses.all()
    # Initialize form based on whether addresses exist
    initial_address_form_data = {} # Start empty
    address_form = AddressForm(initial=initial_address_form_data)
    error = None

    if request.method == 'POST':
        address_choice = request.POST.get('address_choice')
        selected_address = None

        if address_choice == 'existing':
            address_id = request.POST.get('selected_address')
            if address_id:
                try:
                    selected_address = Address.objects.get(id=address_id, user=request.user)
                except Address.DoesNotExist:
                    error = "Invalid address selected."
                    messages.error(request, error)
            else:
                error = "Please select an existing address."
                messages.error(request, error)

        elif address_choice == 'new':
            address_form = AddressForm(request.POST) # Bind POST data
            if address_form.is_valid():
                selected_address = address_form.save(commit=False)
                selected_address.user = request.user
                selected_address.save()
            else:
                error = "Please correct the errors in the new address form."
                # Don't add messages here, form errors will show

        else:
            error = "Please select or add a shipping address."
            messages.error(request, error)

        payment_method = request.POST.get('payment_method', 'COD')

        # Proceed only if no errors and an address is selected/created
        if not error and selected_address:
            # Payment processing simulation or actual logic here
            if payment_method == 'UPI':
                 # In a real app, integrate with a payment gateway
                 # For now, just simulate success or redirect to a payment page
                 request.session['checkout_address_id'] = selected_address.id
                 # Assuming you have a process_payment view/template
                 return render(request, 'cart/process_payment.html', {'cart': cart, 'address': selected_address})


            # --- COD LOGIC (TRANSACTION) ---
            try:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        address=selected_address,
                        total_amount=cart.get_grand_total(),
                        payment_method=payment_method,
                        payment_status=False # COD is not paid yet
                    )

                    for item in cart.items.all():
                        product = item.product
                        if product.stock < item.quantity:
                            # If stock runs out during checkout
                            messages.error(request, f"Sorry, '{product.name}' is now out of stock or insufficient quantity available.")
                            raise ValueError("Insufficient stock") # Rollback transaction

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item.quantity,
                            price=product.price
                        )
                        # Decrease stock
                        product.stock -= item.quantity
                        product.save()

                    cart.items.all().delete() # Clear the cart
                # Transaction successful
                return redirect('order_successful', order_id=order.order_id)
            except ValueError as e:
                 # Catch the stock error, message already sent
                 # Redirect back to cart or checkout to show the error
                 return redirect('view_cart') # Or checkout maybe better?
            # --- END OF COD LOGIC ---

    # If GET request or POST had errors
    context = {
        'cart': cart,
        'addresses': addresses,
        'address_form': address_form, # Pass potentially bound form with errors
        'error': error # Pass generic errors if any
    }
    return render(request, 'cart/checkout.html', context)


@login_required
def order_successful(request, order_id):
    # Ensure the user can only see their own order confirmation
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'cart/order_successful.html', context)
