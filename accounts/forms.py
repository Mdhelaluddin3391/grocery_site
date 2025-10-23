# mdhelaluddin3391/grocery_site/grocery_site-ef56a17f05a0104c110d6d30e8f25e7b4f1e2b3c/accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Address, UserProfile
from django.contrib.auth.models import User
from django.db import transaction

# --- Registration Form ---
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=150, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email.')
    phone_number = forms.CharField(max_length=15, required=True, help_text='Required. Enter a valid phone number.')
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # UserProfile gets created automatically via a signal.
            # We just need to update it with the phone number.
            user.profile.phone_number = self.cleaned_data['phone_number']
            user.profile.save()
            
        return user

# --- Login Form ---
class CustomAuthenticationForm(AuthenticationForm):
    pass

# --- Address Form ---
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

# --- Profile Update Forms ---
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number']