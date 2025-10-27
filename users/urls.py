# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('send-otp/', views.send_otp, name='send_otp'),
    path('login/', views.otp_login_page, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('logout/', views.logout_user, name='logout_user'),
    path('profile/', views.profile_view, name='profile'),
    path('google-login-success/', views.google_login_success, name='google_login_success'),
]
