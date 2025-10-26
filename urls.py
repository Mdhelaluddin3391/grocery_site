# dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home_view, name='dashboard_home'),
    path('login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.staff_logout_view, name='staff_logout'),
]