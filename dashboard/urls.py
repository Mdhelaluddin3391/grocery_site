# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.staff_logout_view, name='staff_logout'),
    path('', views.dashboard_home_view, name='dashboard_home'),
    path('live-orders/', views.live_orders_view, name='live_orders'),
    path('order/<str:order_id>/', views.order_detail_view, name='order_detail'),
    path('packed-orders/', views.packed_orders_view, name='packed_orders'),
    path('delivery-map/', views.delivery_map_view, name='delivery_map'),
    path('customers/', views.customers_view, name='customers'),
    path('finance/', views.finance_view, name='finance'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('order/update-status/<str:order_id>/', views.update_order_status_from_list, name='update_order_status_from_list'),
    path('order/cancel/<str:order_id>/', views.cancel_order_view, name='cancel_order'),
    path('export/orders/', views.export_orders_csv, name='export_orders_csv'),
    path('api/charts/orders-per-hour/', views.orders_per_hour_api, name='api_orders_per_hour'),
    path('api/charts/top-selling-items/', views.top_selling_items_api, name='api_top_selling_items'),
    path('api/charts/monthly-revenue/', views.monthly_revenue_api, name='api_monthly_revenue'),
    path('order/cancel/<str:order_id>/', views.cancel_order_view, name='cancel_order'),
]