from django.db import models

# Create your models here.
# wms/models.py
from django.db import models
from django.conf import settings
from store.models import Product

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(default=0, help_text="Quantity available in the warehouse.")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inventory for {self.product.name}"

    class Meta:
        verbose_name_plural = "Inventories"

class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Adjustment'),
        ('DMG', 'Damaged'),
        ('RET', 'Return'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField() # Positive for IN, Negative for OUT
    remarks = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Staff member who recorded the movement.")

    def __str__(self):
        return f"{self.get_movement_type_display()} of {self.quantity} for {self.product.name} on {self.timestamp.strftime('%Y-%m-%d')}"