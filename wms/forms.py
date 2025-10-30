# wms/forms.py
from django import forms
from .models import StockMovement

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity', 'remarks']
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'w-full p-2 border rounded-md'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-md', 'placeholder': 'Positive for IN, Negative for OUT'}),
            'remarks': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-md', 'rows': 3, 'placeholder': 'Optional notes for the reason...'}),
        }