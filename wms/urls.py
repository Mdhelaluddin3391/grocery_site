# wms/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list_view, name='inventory_list'),
    path('adjust/<int:product_id>/', views.adjust_stock_view, name='adjust_stock'),
]