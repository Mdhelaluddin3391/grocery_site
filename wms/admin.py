# wms/admin.py
from django.contrib import admin
from .models import Vendor, Location, Inventory, PurchaseOrder, PurchaseOrderItem, GoodsReceivedNote, StockMovement

admin.site.register(Vendor)
admin.site.register(Location)
admin.site.register(Inventory)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(GoodsReceivedNote)
admin.site.register(StockMovement)