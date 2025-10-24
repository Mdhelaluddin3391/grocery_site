# accounts/admin.py (FINAL CLEANED CODE)

from django.contrib import admin
from .models import UserProfile, Address # Proxy models ka import hataya gaya
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# --- INLINE: UserProfile ko User ke andar dikhane ke liye ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Details'
    fk_name = 'user'
    fields = ('phone_number', 'address') 


# --- Custom User Admin Class (Jo UserProfile Inline ko jodega) ---
class CustomUserAdmin(UserAdmin):
    # UserAdmin ke default list_display mein phone number jodein
    list_display = UserAdmin.list_display + ('get_phone_number',)
    # inlines mein UserProfileInline jodein
    inlines = [UserProfileInline] 

    # UserProfile se phone number fetch karne ka custom method
    def get_phone_number(self, obj):
        # Superuser ke liye default 'N/A' return karein
        return obj.profile.phone_number if hasattr(obj, 'profile') else 'N/A'
    get_phone_number.short_description = 'Phone Number'


# --- Address Model Admin (Improved) ---
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line_1', 'city', 'pincode', 'address_type', 'is_default')
    list_filter = ('is_default', 'city', 'address_type')
    search_fields = ('user__username', 'address_line_1', 'pincode')
    list_editable = ('is_default',)
    raw_id_fields = ('user',)

# --- Registration ---

# Default User model ko unregister karein taki hum apne custom class ko use kar sakein
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass 

# Ab default User model ko CustomUserAdmin के साथ register karein.
admin.site.register(User, CustomUserAdmin) 

admin.site.register(UserProfile) 
admin.site.register(Address, AddressAdmin)