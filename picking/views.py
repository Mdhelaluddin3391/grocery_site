from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from .models import PickingJob, PickedItem

def staff_check(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(staff_check, login_url='staff_login')
def picker_dashboard_view(request):
    assigned_jobs = PickingJob.objects.filter(picker=request.user, status__in=['Assigned', 'In Progress']).order_by('created_at')
    context = {'assigned_jobs': assigned_jobs}
    return render(request, 'picking/picker_dashboard.html', context)

@user_passes_test(staff_check, login_url='staff_login')
def picking_job_detail_view(request, job_id):
    job = get_object_or_404(PickingJob, id=job_id, picker=request.user)
    if job.status == 'Assigned':
        job.status = 'In Progress'
        job.save()
    return render(request, 'picking/picking_job_detail.html', {'job': job})

@user_passes_test(staff_check, login_url='staff_login')
def mark_item_as_picked_api(request, picked_item_id):
    if request.method == 'POST':
        picked_item = get_object_or_404(PickedItem, id=picked_item_id)
        picked_item.is_picked = True
        picked_item.picked_at = timezone.now()
        picked_item.save()
        job = picked_item.picking_job
        all_items_picked = not job.picked_items.filter(is_picked=False).exists()
        if all_items_picked:
            job.status = 'Completed'
            job.save()
            job.order.status = 'Packed'
            job.order.save()
            return JsonResponse({'status': 'success', 'all_picked': True})
        return JsonResponse({'status': 'success', 'all_picked': False})
    return JsonResponse({'status': 'error'}, status=400)