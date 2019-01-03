from django import forms
from .models import Control

class AddImplementationForm(forms.Form):
    """
    Form for adding implementations
    """
    control = forms.ModelChoiceField(queryset=Control.objects.all())
    