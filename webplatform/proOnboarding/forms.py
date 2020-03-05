from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import proOB
field_choices = [('astro-ph.GA',' Astrophysics of Galaxies'),
                ('astro-ph.CO', ' Cosmology and Nongalactic Astrophysics'),
                ('astro-ph.EP', 'Earth and Planetary Astrophysics'),
                ('astro-ph.HE', 'High Energy Astrophysical Phenomena'),
                ('astro-ph.IM', 'Instrumentation and Methods for Astrophysics'),
                ('astro-ph.SR', 'Solar and Stellar Astrophysics')]
class proOnboard(forms.ModelForm):
    affiliation = forms.CharField(label = 'Enter your affilliated institute', required = True)
    field_of_interest = forms.ChoiceField(choices = field_choices, required = True)

    class Meta:
        model = proOB
        exclude = ['user_id', 'fov']
