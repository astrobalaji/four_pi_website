from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class ObsSettings(forms.Form):

    exposure_time = forms.FloatField(label = 'Desired Exposure time in seconds', widget = forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    further_instructions = forms.CharField(label = 'Further instructions for the amateur astronomer', widget = forms.Textarea(attrs={'style': 'width: 50%', 'cols': 200,}))
