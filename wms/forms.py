# wms/forms.py
from django import forms
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceivedNote, StockMovement

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['vendor', 'po_number', 'expected_delivery_date']
        widgets = {
            'vendor': forms.Select(attrs={'class': 'w-full p-2 border rounded-md'}),
            'po_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded-md', 'type': 'date'}),
        }

class GRNForm(forms.ModelForm):
    class Meta:
        model = GoodsReceivedNote
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-md', 'rows': 3}),
        }

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity', 'remarks']
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'w-full p-2 border rounded-md'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-md', 'placeholder': 'Positive for IN, Negative for OUT'}),
            'remarks': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-md', 'rows': 3, 'placeholder': 'Optional notes for the reason...'}),
        }