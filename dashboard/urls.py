from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.staff_logout_view, name='staff_logout'),
    path('', views.dashboard_home_view, name='dashboard_home'),
]
