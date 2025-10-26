# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CustomerProfile, StaffProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Yeh signal user banne ke baad automatically profile create karega.
    """
    if created: # Sirf tab jab user naya bana ho
        if instance.is_staff:
            # Agar user staff hai, to StaffProfile banayein
            StaffProfile.objects.create(user=instance, employee_id=f"EMP-{instance.id}")
        else:
            # Agar regular user hai, to CustomerProfile banayein
            CustomerProfile.objects.create(user=instance)