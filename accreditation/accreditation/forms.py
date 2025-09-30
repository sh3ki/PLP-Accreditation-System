"""
Authentication Forms for PLP Accreditation System
"""

from django import forms
from django.contrib.auth import authenticate
from accreditation.firebase_auth import FirebaseUser


class LoginForm(forms.Form):
    """Login form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please Enter Your Details',
            'required': True,
        }),
        label='EMAIL'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Please Enter Your Details', 
            'required': True,
        }),
        label='PASSWORD'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Remember Me'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        """Clean and validate form data"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            self.user = FirebaseUser.authenticate(email, password)
            if not self.user:
                raise forms.ValidationError(
                    "Invalid email or password. Please try again."
                )
            
            if not self.user.is_active:
                raise forms.ValidationError(
                    "This account has been deactivated."
                )
        
        return cleaned_data
    
    def get_user(self):
        """Get authenticated user"""
        return self.user