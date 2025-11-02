"""
Authentication Forms for PLP Accreditation System
"""

from django import forms
from django.contrib.auth import authenticate
from accreditation.firebase_auth import FirebaseUser
from accreditation.firebase_utils import get_all_documents


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
        self.auth_result = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        """Clean and validate form data"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            self.auth_result = FirebaseUser.authenticate(email, password)
            
            if self.auth_result.get('success'):
                self.user = self.auth_result.get('user')
            else:
                error_type = self.auth_result.get('error')
                message = self.auth_result.get('message')
                
                # Store auth result for later use
                if error_type == 'account_locked':
                    self.locked_until = self.auth_result.get('locked_until')
                    self.remaining_seconds = self.auth_result.get('remaining_seconds')
                elif error_type == 'account_deactivated':
                    self.is_deactivated = True
                
                raise forms.ValidationError(message)
        
        return cleaned_data
    
    def get_user(self):
        """Get authenticated user"""
        return self.user
    
    def get_auth_result(self):
        """Get full authentication result"""
        return self.auth_result


class UserManagementForm(forms.Form):
    """Form for creating and editing users"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name',
            'required': True,
        }),
        label='First Name'
    )
    
    middle_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter middle name (optional)',
        }),
        label='Middle Name'
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name',
            'required': True,
        }),
        label='Last Name'
    )
    
    email_prefix = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email prefix (e.g., john.doe)',
            'required': True,
        }),
        label='Email',
        help_text='Will be combined with @plpasig.edu.ph'
    )
    
    department = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        }),
        label='Department'
    )
    
    role = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        }),
        label='Role'
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        }),
        label='Status',
        initial='active'
    )
    
    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        
        # Load departments from database
        try:
            departments = get_all_documents('departments')
            dept_choices = [('', 'Select Department')]
            for dept in departments:
                if dept.get('is_active', True):
                    dept_choices.append((dept.get('code'), dept.get('name')))
            self.fields['department'].choices = dept_choices
        except Exception as e:
            print(f"Error loading departments: {e}")
            self.fields['department'].choices = [('', 'Select Department')]
        
        # Load roles from database
        try:
            roles = get_all_documents('roles')
            role_choices = [('', 'Select Role')]
            for role in roles:
                if role.get('is_active', True):
                    role_choices.append((role.get('code'), role.get('name')))
            self.fields['role'].choices = role_choices
        except Exception as e:
            print(f"Error loading roles: {e}")
            self.fields['role'].choices = [('', 'Select Role')]
    
    def clean_email_prefix(self):
        """Validate and clean email prefix"""
        email_prefix = self.cleaned_data.get('email_prefix')
        if email_prefix:
            # Remove spaces and convert to lowercase
            email_prefix = email_prefix.lower().strip().replace(' ', '.')
            # Remove any @ symbols if user included them
            email_prefix = email_prefix.replace('@', '')
            # Basic validation
            if not email_prefix:
                raise forms.ValidationError('Email prefix cannot be empty.')
        return email_prefix