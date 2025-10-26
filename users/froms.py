# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Address

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('phone_number', 'name')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Phone Number", max_length=15)

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_type', 'address_line_1', 'address_line_2', 'city', 'state', 'pincode', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }