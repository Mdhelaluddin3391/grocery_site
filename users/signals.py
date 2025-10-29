from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CustomerProfile, StaffProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Yeh signal naye user ke liye automatically sahi profile banata hai.
    - Agar user superuser hai -> StaffProfile banega jismein "ADMIN-" ID hogi.
    - Agar user staff hai (lekin superuser nahi) -> StaffProfile banega jismein "EMP-" ID hogi.
    - Agar user customer hai -> CustomerProfile banega.
    """
    if not created:
        return

    # Superuser ke liye alag se handle karein
    if instance.is_superuser:
        StaffProfile.objects.get_or_create(
            user=instance,
            defaults={'employee_id': f"ADMIN-{instance.id}", 'role': 'Administrator'}
        )
        return

    # Staff ke liye handle karein
    if instance.is_staff:
        StaffProfile.objects.get_or_create(
            user=instance,
            defaults={'employee_id': f"EMP-{instance.id}", 'role': 'Staff'}
        )
        return

    # Customer ke liye handle karein
    if getattr(instance, 'is_customer', False):
        CustomerProfile.objects.create(user=instance)