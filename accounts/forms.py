# accounts/forms.py

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Django ke bane-banaye UserCreationForm ko istemal karenge
class CustomUserCreationForm(UserCreationForm):
    pass

# Django ke bane-banaye AuthenticationForm ko istemal karenge
class CustomAuthenticationForm(AuthenticationForm):
    pass