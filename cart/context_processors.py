# cart/context_processors.py

from .models import Cart

def cart_item_count(request):
    if request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
            item_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            item_count = 0
        return {'cart_item_count': item_count}
    return {'cart_item_count': 0}