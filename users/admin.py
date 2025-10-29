# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'phone_number', 'name', 'is_staff', 'is_superuser', 'is_customer')
    list_filter = ('is_staff', 'is_superuser', 'is_customer', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_customer', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone_number', 'password', 'password2', 'is_customer', 'is_staff')
        }),
    )
    search_fields = ('email', 'phone_number', 'name')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)