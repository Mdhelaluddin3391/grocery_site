# accounts/urls.py

from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.phone_login, name='login'),
    path('otp-verify/', views.otp_verify, name='otp_verify'),
    path('profile/', views.profile_view, name='profile'),
    # Yahan 'user_logout' ko 'customer_logout' se badla gaya hai
    path('logout/', views.customer_logout, name='logout'),
    path('delete/', views.delete_account, name='delete_account'),
]