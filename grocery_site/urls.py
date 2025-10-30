# grocery_site/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('cart/', include('cart.urls')),
    path('wms/', include('wms.urls')),
    path('riders/', include('riders.urls')),
    path('picking/', include('picking.urls')), # <-- YEH LINE ADD KAREIN
    path('', include('store.urls')),
]