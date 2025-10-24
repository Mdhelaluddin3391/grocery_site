# store/admin.py (FINAL UPDATED CODE)

from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # list_display mein parent category ko dikhayein
    list_display = ('name', 'parent', 'show_on_homepage', 'order', 'sales_priority')
    list_filter = ('parent', 'show_on_homepage')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} 
    list_editable = ('order', 'sales_priority', 'show_on_homepage') # Order aur priority ko list se edit karein

    # Category hierarchy ko dikhane ke liye behtar fieldsets
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'parent', 'icon'),
        }),
        ('Display Settings', {
            'fields': ('show_on_homepage', 'order', 'sales_priority'),
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # list_display mein naye fields aur stock/price ko shamil karein
    list_display = ('name', 'category', 'price', 'old_price', 'stock', 'discount', 'is_special', 'is_hot')
    list_filter = ('category', 'is_special', 'is_hot', 'stock')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_special', 'is_hot') # List se hi price, stock, aur status badal sakte hain
    prepopulated_fields = {'slug': ('name',)}
    
    # Detail view mein fields ko groups mein baant dein
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'slug', 'description'),
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'old_price', 'discount', 'stock'),
        }),
        ('Display & Details', {
            'fields': ('image', 'quantity', 'time', 'is_special', 'is_hot'),
        }),
    )