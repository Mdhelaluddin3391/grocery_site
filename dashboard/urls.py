# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.staff_logout_view, name='staff_logout'),
    path('', views.dashboard_home_view, name='dashboard_home'),
    
    # --- YEH BADLAV HUA HAI ---
    path('live-orders/', views.live_orders_view, name='live_orders'),
    path('inventory/', views.wms_view, name='inventory'),
    # --------------------------

    path('order/<str:order_id>/', views.order_detail_view, name='order_detail'),
    path('delivery-map/', views.dashboard_home_view, name='delivery_map'),
    path('customers/', views.dashboard_home_view, name='customers'),
    path('riders/', views.dashboard_home_view, name='riders'),
    path('finance/', views.dashboard_home_view, name='finance'),
    path('analytics/', views.dashboard_home_view, name='analytics'),
]