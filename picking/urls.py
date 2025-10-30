# picking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.picker_dashboard_view, name='picker_dashboard'),
]