from django import forms
from .models import ReturnRequest

from django import forms

class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label='', 
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'required': 'required'
            
        })
    )
