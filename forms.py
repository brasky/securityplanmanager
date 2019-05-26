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
    similar_team = forms.ModelChoiceField(queryset=Team.objects.all(), required=False)
    class Meta:
        model = Team
        fields = ['name']

    def save(self, commit=True):
        similar_team = self.cleaned_data['similar_team']
        if similar_team:  
            team_object = super(AddTeamForm, self).save(commit=commit)
            implementations = similar_team.implementations.all()
            for implementation in implementations:
                implementation.teams.add(team_object)
            return team_object
        else:
            return super(AddTeamForm, self).save(commit=commit)

class SSPUploadForm(forms.Form):
    file = forms.FileField()
    certification = forms.ModelChoiceField(queryset=Certification.objects.all())
    