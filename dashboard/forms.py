# dashboard/forms.py
from django import forms
from allauth.socialaccount.forms import SignupForm

class StaffSocialSignupForm(SignupForm):
    """
    Custom sign-up form jab naya staff Google se sign up karega.
    """
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    def clean(self):
        """
        Check karein ki dono password match karte hain ya nahi.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, request):
        """
        User ko save karte waqt password set karein aur use staff banayein.
        """
        user = super().save(request)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True
        user.is_customer = False
        user.save()
        return user