# cart/context_processors.py (FINAL CODE - Customer Session)

from .models import Cart
from accounts.models import Customer
from django.shortcuts import get_object_or_404

def cart_item_count(request):
    # Pehle check karo ki Customer session mein hai ya nahi
    if 'customer_id' in request.session:
        try:
            # Customer ID se Customer object dhundo
            customer = get_object_or_404(Customer, id=request.session['customer_id'])
            # Us customer ka cart dhundo
            cart = Cart.objects.get(customer=customer)
            item_count = sum(item.quantity for item in cart.items.all())
        except (Cart.DoesNotExist, Customer.DoesNotExist):
            item_count = 0
        return {'cart_item_count': item_count}
    # Agar customer login nahi hai, to count 0 rakho
    return {'cart_item_count': 0}