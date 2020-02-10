from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import proOB
field_choices = [('yso','Young Stellar Objects'), ('planets', 'Planets'), ('exop', 'Exoplanets'), ('agn', 'Active Galactic Nucleii'), ('galactic', 'Galaxies'), ('extragal', 'Extra Galactic'), ('cosmology', 'Cosmology')]
class proOnboard(forms.ModelForm):
    affiliation = forms.CharField(label = 'Enter your affilliated institute', required = True)
    field_of_interest = forms.ChoiceField(choices = field_choices, required = True)

    class Meta:
        model = proOB
        exclude = ['user_id', 'fov']
