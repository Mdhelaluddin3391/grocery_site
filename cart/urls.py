from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # New URLs for quantity management
    path('increment/<int:item_id>/', views.increment_cart_item, name='increment_cart_item'),
    path('decrement/<int:item_id>/', views.decrement_cart_item, name='decrement_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-successful/<str:order_id>/', views.order_successful, name='order_successful'),
]