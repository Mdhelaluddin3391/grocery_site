# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('order/<str:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),
    path('order/update_status/<str:order_id>/', views.update_order_status, name='update_order_status'),
]