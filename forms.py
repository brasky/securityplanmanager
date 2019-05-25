from django import forms
from django.forms import ModelForm
from django.forms import modelformset_factory
from django.forms import BaseModelFormSet
from .models import Control, Implementation, Certification, Team


class AddImplementationForm(ModelForm):
    """
    Form for adding implementations
    """

    class Meta:
        model = Implementation
        fields = ['control', 'parameter', 'customer_responsibility',
                  'solution', 'implementation_status', 'control_origination', 'teams']

class EditImplementationsFormSet(BaseModelFormSet):
    def __init__(self, *args, control, **kwargs):       
        super(EditImplementationsFormSet, self).__init__(*args, **kwargs)
        self.queryset = Implementation.objects.filter(control=control)
        self.control = control

class AddCertificationForm(ModelForm):

    class Meta:
        model = Certification
        fields = ['name', 'controls']

class AddTeamForm(ModelForm):

    class Meta:
        model = Team
        fields = ['name']

class SSPUploadForm(forms.Form):
    file = forms.FileField()
    certification = forms.ModelChoiceField(queryset=Certification.objects.all())
    