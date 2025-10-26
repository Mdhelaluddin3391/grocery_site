# cart/admin.py

from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ('get_product_price',)

    def get_product_price(self, obj):
        return obj.product.price
    get_product_price.short_description = 'Price Per Item'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ('product', 'quantity', 'price') 

class OrderAdmin(admin.ModelAdmin):
    # 'user' ko 'customer' se badla gaya hai
    list_display = ['order_id', 'customer', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_id', 'customer__phone_number', 'shipping_address']
    inlines = [OrderItemInline]
    # 'user' ko 'customer' se badla gaya hai
    readonly_fields = ('order_id', 'customer', 'total_amount', 'created_at', 'updated_at', 'shipping_address')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'customer', 'total_amount', 'created_at', 'updated_at'),
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_method', 'payment_status'),
        }),
        ('Shipping Details', {
            'fields': ('shipping_address',),
        }),
    )

class CartAdmin(admin.ModelAdmin):
    # 'user' ko 'customer' se badla gaya hai
    list_display = ['customer', 'created_at', 'get_total_items', 'get_subtotal', 'get_grand_total']
    inlines = [CartItemInline]
    readonly_fields = ('created_at',)
    search_fields = ['customer__phone_number']
    
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)