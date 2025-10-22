# cart/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from django.contrib.auth.decorators import login_required
from store.views import get_main_categories
from django.db import transaction

# ... add_to_cart, view_cart, remove_from_cart views waise hi rahenge ...

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_item_count': cart.get_total_items()})
    
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

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    # Agar cart khali hai to redirect karein
    if not cart_items:
        return redirect('view_cart')

    # transaction.atomic ensures that all database operations are completed successfully
    # Agar koi bhi operation fail hota hai, to saare changes aapis aa jayenge
    with transaction.atomic():
        # User ka address get karein, ya default address istemal karein
        shipping_address = request.user.profile.address or "Default Address, Please Update"

        # Naya Order banayein
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=cart.get_grand_total(),
            payment_method='COD' # Abhi ke liye Cash on Delivery
        )

        # Cart items ko Order items mein convert karein
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Cart ko khali kar dein
        cart.items.all().delete()

    # Order successful page par redirect karein
    return redirect('order_successful', order_id=order.order_id)


@login_required
def order_successful(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    context = {
        'order': order,
        'main_categories': get_main_categories(),
    }
    return render(request, 'cart/order_successful.html', context)