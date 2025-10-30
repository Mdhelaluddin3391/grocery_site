from django.db import models
from django.conf import settings

class RiderProfile(models.Model):
    STATUS_CHOICES = [
        ('OFFLINE', 'Offline'),
        ('AVAILABLE', 'Available'),
        ('ON_DELIVERY', 'On Delivery'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='riderprofile')
    vehicle_id = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., TS01AB1234")
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OFFLINE')
    last_known_latitude = models.CharField(max_length=50, blank=True, null=True)
    last_known_longitude = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rider: {self.user.name or self.user.email}"

    class Meta:
        verbose_name_plural = "Rider Profiles"