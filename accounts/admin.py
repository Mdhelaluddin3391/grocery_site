from django.contrib import admin
from .models import UserProfile, Address # Address ko import karein

# Address model ke liye ek custom admin class (Optional, lekin behtar hai)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line_1', 'city', 'pincode', 'is_default')
    list_filter = ('is_default', 'city', 'state')
    search_fields = ('user__username', 'address_line_1', 'pincode')

# Apne models ko yahan register karein
admin.site.register(UserProfile)
admin.site.register(Address, AddressAdmin) # Address model ko register karein