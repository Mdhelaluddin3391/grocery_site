# dashboard/admin.py
from django.contrib import admin
from .models import AuthorizedStaff

@admin.register(AuthorizedStaff)
class AuthorizedStaffAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'created_at')
    search_fields = ('email', 'name', 'role')
    list_filter = ('role',)
    ordering = ('-created_at',)