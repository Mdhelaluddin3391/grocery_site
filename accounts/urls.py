# accounts/urls.py

from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView # Django ke default LogoutView ka istemal kar sakte hain

urlpatterns = [
    path('login/', views.phone_login, name='login'), # Phone number input
    path('otp-verify/', views.otp_verify, name='otp_verify'), # OTP verification
    path('profile/', views.profile_view, name='profile'), # User profile
    path('logout/', views.user_logout, name='logout'), # Logout view
    path('delete/', views.delete_account, name='delete_account'), # Account delete
]