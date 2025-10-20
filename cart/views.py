# cart/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product
from django.contrib.auth.decorators import login_required
from store.views import get_main_categories # <-- Yeh import karein

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # User ko wapis usi page par bhejo jahan se usne "ADD" click kiya tha
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = sum(item.get_subtotal() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'main_categories': get_main_categories(), # <-- Context mein add karein
    }
    return render(request, 'cart/cart_detail.html', context)

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')