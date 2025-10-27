# grocery_site/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # <-- Google login flow ke liye
    path('', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('users.urls')), # <-- Yeh user profile/logout ke liye hai
    path('dashboard/', include('dashboard.urls')),
]