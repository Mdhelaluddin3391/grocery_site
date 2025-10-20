# cart/context_processors.py

from .models import Cart

def cart_item_count(request):
    # Pehle check karo ki user login hai ya nahi
    if request.user.is_authenticated:
        try:
            # User ka cart dhundo
            cart = Cart.objects.get(user=request.user)
            # Cart ke sabhi items ki quantity ko jod do
            item_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            item_count = 0
        return {'cart_item_count': item_count}
    # Agar user login nahi hai, to count 0 rakho
    return {'cart_item_count': 0}