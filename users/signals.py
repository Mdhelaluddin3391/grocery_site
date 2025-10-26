# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CustomerProfile, StaffProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            StaffProfile.objects.create(user=instance, employee_id=f"EMP-{instance.id}")
        else:
            CustomerProfile.objects.create(user=instance)