# accounts/admin.py (FINAL UPDATED CODE)

from django.contrib import admin
from .models import UserProfile, Address, StaffAccount, CustomerAccount # CustomerAccount ko import karein
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# --- INLINE: UserProfile ko User ke andar dikhane ke liye ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Details'
    fk_name = 'user'
    # Profile mein sirf phone number aur address ko edit karne ki anumati
    fields = ('phone_number', 'address') 


# --- Admin Class for Staff Accounts (pichle step se thoda sa update) ---
class StaffAccountAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'last_login')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    inlines = [UserProfileInline] # Staff ke profile ko bhi dikhao

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True)

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        if not change:
            obj.is_superuser = False
        super().save_model(request, obj, form, change)


# --- NAYA CODE: Admin Class for Customer Accounts (Non-Staff) ---
class CustomerAccountAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'last_login', 'get_phone_number')
    list_filter = ('is_active', 'is_superuser')
    search_fields = ('username', 'email', 'userprofile__phone_number') # Profile se search karein
    ordering = ('username',)
    inlines = [UserProfileInline] # Customer profile ko yahan jodein

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info & Contact', {'fields': ('first_name', 'last_name', 'email')}),
        ('Status', {'fields': ('is_active',)}), 
    )
    
    # UserProfile se phone number fetch karne ka custom method
    def get_phone_number(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else 'N/A'
    get_phone_number.short_description = 'Phone Number'

    # QuerySet ko filter karein (Sirf non-staff users)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=False)

    # Naye user banate waqt is_staff ko False set karein
    def save_model(self, request, obj, form, change):
        obj.is_staff = False
        obj.is_superuser = False
        super().save_model(request, obj, form, change)


# --- Address Model Admin (Improved) ---
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line_1', 'city', 'pincode', 'address_type', 'is_default')
    list_filter = ('is_default', 'city', 'address_type')
    search_fields = ('user__username', 'address_line_1', 'pincode')
    list_editable = ('is_default',) # List se hi default status badal sakte hain
    raw_id_fields = ('user',)

# --- Registration ---

# Default User model ko unregister karein taki hum apne custom models ko use kar sakein
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass 

# Ab Admin Panel mein 'Customer Accounts' aur 'Staff Accounts' do alag sections honge.
admin.site.register(UserProfile) # UserProfile ko alag se rakhein
admin.site.register(Address, AddressAdmin)
admin.site.register(StaffAccount, StaffAccountAdmin)
admin.site.register(CustomerAccount, CustomerAccountAdmin)