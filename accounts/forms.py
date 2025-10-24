# mdhelaluddin3391/grocery_site/grocery_site-b7c9b0ae8a697f4fa8e0b4620ececbe3ab919e2a/accounts/forms.py

from django import forms
from .models import Address, UserProfile
from django.contrib.auth.models import User

# --- Naye Login/Signup Forms ---
class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your 10-digit phone number'}))

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP'}))


# --- Profile aur Address se Jude Zaroori Forms ---

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

# User ke profile (naam, email) update karne ke liye
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

# User ka phone number update karne ke liye
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = []