from django import forms
from .models import EmailConfiguration

class EmailConfigurationForm(forms.ModelForm):
    """Form for creating and updating email configurations"""
    class Meta:
        model = EmailConfiguration
        fields = [
            'name', 'sender_email', 'sender_password',
            'receiver_email', 'receiver_password',
            'smtp_server', 'smtp_port', 'imap_server', 'imap_port',
            'check_interval', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sender_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sender_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'receiver_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'receiver_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'smtp_server': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'imap_server': forms.TextInput(attrs={'class': 'form-control'}),
            'imap_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'check_interval': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RunCheckForm(forms.Form):
    """Form for running an immediate check"""
    configuration = forms.ModelChoiceField(
        queryset=EmailConfiguration.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label=None
    )
