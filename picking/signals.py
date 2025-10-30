# picking/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from cart.models import Order
from users.models import CustomUser
from .models import PickingJob, PickedItem

@receiver(post_save, sender=Order)
def create_and_assign_picking_job(sender, instance, created, **kwargs):
    """
    Naya order aane par PickingJob banata hai aur automatically ek
    available picker ko assign kar deta hai.
    """
    if created and instance.status == 'Pending':
        # Step 1: Naye order ke liye PickingJob banayein
        picking_job = PickingJob.objects.create(order=instance)
        
        # Step 2: Order ke har item ke liye PickedItem record banayein
        for order_item in instance.items.all():
            PickedItem.objects.create(
                picking_job=picking_job,
                order_item=order_item
            )

        # Step 3: Ek available picker ko dhoondein
        # Abhi ke liye, hum pehle available staff ko le rahe hain jo superuser nahi hai.
        # Future mein hum 'is_available' jaisa status add kar sakte hain.
        available_picker = CustomUser.objects.filter(
            is_staff=True, 
            is_superuser=False
        ).first() # Pehla available picker

        # Step 4: Agar picker milta hai, to use assign karein aur status update karein
        if available_picker:
            picking_job.picker = available_picker
            picking_job.status = 'Assigned'
            picking_job.save()

            # Order ka status 'Processing' karein
            instance.status = 'Processing'
            instance.save()