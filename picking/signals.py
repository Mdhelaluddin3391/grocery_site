# picking/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction  # <-- YEH LINE ADD KAREIN
from cart.models import Order
from users.models import CustomUser
from .models import PickingJob, PickedItem

def actual_job_creation_logic(order_pk):
    """
    Yeh function tab chalega jab transaction safal ho jayega.
    """
    try:
        instance = Order.objects.get(pk=order_pk)
        
        # Step 1: Naye order ke liye PickingJob banayein
        picking_job, created = PickingJob.objects.get_or_create(order=instance)
        if not created:
            return # Job pehle se hai, kuch na karein

        # Step 2: Order ke har item ke liye PickedItem record banayein
        for order_item in instance.items.all():
            PickedItem.objects.create(
                picking_job=picking_job,
                order_item=order_item
            )

        # Step 3: Ek available picker ko dhoondein
        available_picker = CustomUser.objects.filter(
            is_staff=True,
            is_superuser=False
        ).first()

        # Step 4: Agar picker milta hai, to use assign karein
        if available_picker:
            picking_job.picker = available_picker
            picking_job.status = 'Assigned'
            picking_job.save()

            # Order ka status 'Processing' karein
            instance.status = 'Processing'
            instance.picker = available_picker
            instance.save(update_fields=['status', 'picker'])

    except Order.DoesNotExist:
        pass # Agar order exist nahi karta to kuch na karein


@receiver(post_save, sender=Order)
def create_and_assign_picking_job(sender, instance, created, **kwargs):
    """
    Naya order aane par, transaction commit hone ke baad job creation ko trigger karta hai.
    """
    if created and instance.status == 'Pending':
        # Mukhya logic ko transaction commit hone ke baad chalayein
        transaction.on_commit(lambda: actual_job_creation_logic(instance.pk))