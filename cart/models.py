from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from decimal import Decimal

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    handling_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_subtotal(self):
        # Calculation remains the same
        return sum(item.get_subtotal() for item in self.items.all())

    def get_grand_total(self):
        # Calculation remains the same
        subtotal = self.get_subtotal()
        total = subtotal + self.delivery_charge + self.handling_fee - self.discount_amount
        return max(total, Decimal('0.00'))

    # --- NEW METHODS ---
    def get_total_items(self):
        """Calculates the total number of items (sum of quantities)."""
        return sum(item.quantity for item in self.items.all())

    def get_data_for_json(self):
        """Returns a dictionary of all necessary cart data for JS."""
        return {
            'cart_subtotal': self.get_subtotal(),
            'cart_grand_total': self.get_grand_total(),
            'cart_item_count': self.get_total_items(),
        }

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart for {self.cart.user.username}"

    def get_subtotal(self):
        return self.product.price * self.quantity