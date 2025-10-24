# cart/admin.py (FINAL UPDATED CODE)

from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline): # Cart Item ko Cart ke andar dikhane ke liye
    model = CartItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ('get_product_price',) # Product price ko sirf dekhne ki anumati

    def get_product_price(self, obj):
        return obj.product.price
    get_product_price.short_description = 'Price Per Item'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    # OrderItem mein quantity aur price (jis price par order hua) ko readonly rakhein
    readonly_fields = ('product', 'quantity', 'price') 

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_id', 'user__username', 'shipping_address']
    inlines = [OrderItemInline]
    # Admin ko total amount aur user ko badalne ki anumati na ho
    readonly_fields = ('order_id', 'user', 'total_amount', 'created_at', 'updated_at', 'shipping_address')
    
    # Detail view mein fields ko groups mein baant dein
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'total_amount', 'created_at', 'updated_at'),
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_method', 'payment_status'),
        }),
        ('Shipping Details', {
            'fields': ('shipping_address',),
        }),
    )

class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'get_total_items', 'get_subtotal', 'get_grand_total']
    inlines = [CartItemInline]
    readonly_fields = ('created_at',)
    search_fields = ['user__username']
    
    # get_total_items, get_subtotal, aur get_grand_total Cart model se aa rahe hain
    # (Yeh maana ja raha hai ki aapne Cart model mein yeh methods rakhe hain)

# Admin Panel mein Models Register karein
admin.site.register(Cart, CartAdmin)
# CartItem ko list se hata rahe hain, kyunki woh Cart inline mein dikhega
# admin.site.register(CartItem) 
admin.site.register(Order, OrderAdmin)
# OrderItem ko list se hata rahe hain, kyunki woh Order inline mein dikhega
# admin.site.register(OrderItem)