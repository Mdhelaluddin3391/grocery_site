# cart/models.py

from django.db import models
from store.models import Product
from decimal import Decimal
from django.conf import settings # Ise import karein

class Cart(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    handling_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Cart for session {self.session_key}"

    def get_subtotal(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_grand_total(self):
        subtotal = self.get_subtotal()
        total = subtotal + self.delivery_charge + self.handling_fee - self.discount_amount
        return max(total, Decimal('0.00'))

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def get_data_for_json(self):
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
        return f"{self.quantity} x {self.product.name}"

    def get_subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = (('Pending', 'Pending'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'))
    PAYMENT_CHOICES = (('COD', 'Cash on Delivery'), ('Online', 'Online'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey('users.Address', on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=120, unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='COD')
    payment_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # shipping_address field ki zaroorat nahi agar Address model hai
    # shipping_address = models.TextField() 

    def __str__(self):
        return f"Order {self.order_id}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and not self.order_id:
            timestamp = self.created_at.strftime('%Y%m%d')
            self.order_id = f"ORDER-{timestamp}-{self.id}"
            self.save(update_fields=['order_id'])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Order {self.order.order_id}"

    def get_subtotal(self):
        return self.quantity * self.price