# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Address # Address model ko import karein

# Django ke bane-banaye UserCreationForm ko istemal karenge
class CustomUserCreationForm(UserCreationForm):
    pass

# Django ke bane-banaye AuthenticationForm ko istemal karenge
class CustomAuthenticationForm(AuthenticationForm):
    pass


# --- NAYA ADDRESS FORM ---
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'pincode', 'address_type']
        widgets = {
            'address_line_1': forms.TextInput(attrs={'placeholder': 'House No., Building Name'}),
            'address_line_2': forms.TextInput(attrs={'placeholder': 'Road Name, Area, Colony'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'placeholder': '6-digit Pincode'}),
        }