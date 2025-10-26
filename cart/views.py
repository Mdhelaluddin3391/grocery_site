# cart/views.py

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from django.db import transaction
from django.contrib import messages
from store.views import get_main_categories

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


def add_to_cart(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
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


def view_cart(request):
    cart = get_cart(request)
    context = {
        'cart': cart,
        'main_categories': get_main_categories(),
    }
    return render(request, 'cart/cart_detail.html', context)

def remove_from_cart(request, item_id):
    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item_id_for_json = cart_item.id
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_data = cart.get_data_for_json()
        cart_data.update({'item_removed': True, 'item_id': item_id_for_json})
        return JsonResponse(cart_data)

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

def checkout(request):
    cart = get_cart(request)
    if not cart.items.all().exists():
        return redirect('view_cart')

    if request.method == 'POST':
        # For simplicity, we are not handling address form here.
        # You can add a simple form to get address if needed.
        shipping_address = "Dummy Address for now"
        payment_method = request.POST.get('payment_method', 'COD')

        with transaction.atomic():
            order = Order.objects.create(
                shipping_address=shipping_address,
                total_amount=cart.get_grand_total(),
                payment_method=payment_method,
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
        
    return render(request, 'cart/checkout.html', { 'cart': cart })

def order_successful(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order': order,
        'main_categories': get_main_categories(),
    }
    return render(request, 'cart/order_successful.html', context)