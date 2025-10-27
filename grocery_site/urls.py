from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Customer authentication (OTP-based)
    path('users/', include('users.urls')),

    # Staff/Admin Google Sign-In (django-allauth)
    path('accounts/', include('allauth.urls')),

    # Staff Dashboard routes
    path('dashboard/', include('dashboard.urls')),

    # Cart app
    path('cart/', include('cart.urls')),

    # Storefront (Home + Categories + Product pages)
    path('', include('store.urls')),
]

# Static and Media settings for development
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(getattr(settings, 'MEDIA_URL', '/media/'), document_root=getattr(settings, 'MEDIA_ROOT', ''))
