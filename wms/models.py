# wms/models.py
from django.db import models
from django.conf import settings
from store.models import Product

class Vendor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="A unique name for the location, e.g., A-01-01")
    zone = models.CharField(max_length=50, blank=True, help_text="e.g., Zone A, Frozen Zone")
    rack = models.CharField(max_length=50, blank=True, help_text="e.g., Rack 01")
    bin = models.CharField(max_length=50, blank=True, help_text="e.g., Bin 01")
    capacity = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'location', 'batch_number')
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"{self.product.name} at {self.location.name} - Qty: {self.quantity}"

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')]
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    po_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField()

    def __str__(self):
        return self.po_number

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for PO {self.purchase_order.po_number}"

class GoodsReceivedNote(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT)
    grn_number = models.CharField(max_length=50, unique=True)
    received_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.grn_number

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
    quantity = models.IntegerField()
    remarks = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Staff member who recorded the movement.")
    grn = models.ForeignKey(GoodsReceivedNote, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"{self.get_movement_type_display()} of {self.quantity} for {self.product.name} on {self.timestamp.strftime('%Y-%m-%d')}"