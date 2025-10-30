# riders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.rider_dashboard_view, name='rider_dashboard'),
    # --- YEH NAYI LINE ADD KI GAYI HAI ---
    path('api/locations/', views.get_rider_locations_api, name='api_get_rider_locations'),
    path('app/', views.rider_app_dashboard_view, name='rider_app_dashboard'),
    path('app/deliver/<str:order_id>/', views.mark_as_delivered_view, name='mark_as_delivered'),
    path('assign-delivery/<str:order_id>/', views.assign_rider_view, name='assign_rider'),
    path('assign-delivery/<str:order_id>/', views.assign_rider_view, name='assign_rider'),
    path('app/deliver/<str:order_id>/', views.mark_as_delivered_view, name='mark_as_delivered'),
]