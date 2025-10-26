from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, CustomerProfile, StaffProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create exactly the right profile:
    - If instance.is_staff is True -> StaffProfile
    - If instance.is_customer is True -> CustomerProfile
    We avoid creating a CustomerProfile for staff/superusers.
    """
    if not created:
        return

    # Create staff profile if user is staff
    if instance.is_staff:
        StaffProfile.objects.create(user=instance, employee_id=f"EMP-{instance.id}")
        return

    # Create customer profile only if explicitly is_customer
    if getattr(instance, 'is_customer', False):
        CustomerProfile.objects.create(user=instance)
