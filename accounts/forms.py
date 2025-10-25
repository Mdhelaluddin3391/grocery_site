# accounts/forms.py

from django import forms
from .models import Address, User

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter 10 digit Phone Number', 'required': 'required'}),
        label='Phone Number'
    )

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter OTP', 'required': 'required'}),
        label='OTP'
    )

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user', 'is_default', 'latitude', 'longitude']
        widgets = {
            'address_line_1': forms.TextInput(attrs={'placeholder': 'House No., Building, Street'}),
            'address_line_2': forms.TextInput(attrs={'placeholder': 'Area, Colony, Landmark'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'pincode': forms.TextInput(attrs={'placeholder': 'Pincode'}),
        }