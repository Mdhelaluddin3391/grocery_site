# picking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.picker_dashboard_view, name='picker_dashboard'),
    path('job/<int:job_id>/', views.picking_job_detail_view, name='picking_job_detail'),
    path('api/pick-item/<int:picked_item_id>/', views.mark_item_as_picked_api, name='mark_item_as_picked'),
]