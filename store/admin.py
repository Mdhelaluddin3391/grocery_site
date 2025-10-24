from django.contrib import admin

# Register your models here.
# store/admin.py (UPDATED)

from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'show_on_homepage', 'order')
    list_filter = ('parent', 'show_on_homepage')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} # Slug apne aap ban jayega

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_special')
    list_filter = ('category', 'is_special', 'stock')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock') # List se hi price aur stock badal sakte hain
    prepopulated_fields = {'slug': ('name',)}