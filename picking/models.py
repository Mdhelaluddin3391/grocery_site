from django.db import models

# Create your models here.
# picking/models.py
from django.db import models
from django.conf import settings
from cart.models import Order, OrderItem

class PickingJob(models.Model):
    STATUS_CHOICES = (
        ('Unassigned', 'Unassigned'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='picking_job')
    picker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='picking_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unassigned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Picking Job for Order #{self.order.order_id}"

class PickedItem(models.Model):
    picking_job = models.ForeignKey(PickingJob, on_delete=models.CASCADE, related_name='picked_items')
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE)
    is_picked = models.BooleanField(default=False)
    picked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_item.product.name} - {'Picked' if self.is_picked else 'Not Picked'}"