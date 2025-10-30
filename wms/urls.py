# wms/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list_view, name='inventory_list'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/<int:po_id>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:po_id>/receive/', views.receive_goods, name='receive_goods'),
]