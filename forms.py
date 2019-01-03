from django import forms
from django.forms import ModelForm

from .models import Control, Implementation

class AddImplementationForm(ModelForm):
    """
    Form for adding implementations
    """

    class Meta:
        model = Implementation
        fields = ['control', 'parameter', 'customer_responsibility', 'solution', 'implementation_status', 'control_origination', 'teams']