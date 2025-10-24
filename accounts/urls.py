# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- New OTP Login/Signup URLs ---
    path('login/', views.phone_login, name='login'), # The main login URL now points to the phone number entry page
    path('verify/', views.verify_otp, name='verify_otp'),

    # --- User Profile and Management URLs ---
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- Address Management ---
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('address/set_default/<int:address_id>/', views.set_default_address, name='set_default_address'),
    
    # --- Order and Profile Editing ---
    path('order/<str:order_id>/', views.order_detail_view, name='order_detail'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/delete/', views.delete_profile_view, name='delete_profile'),
    path('staff-login/', views.staff_login_view, name='staff_login'),
]