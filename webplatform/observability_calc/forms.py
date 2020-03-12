from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class ObsSettings(forms.Form):

    exposure_time = forms.FloatField(label = 'Enter your Desired Exposure time in seconds')
    further_instructions = forms.CharField(label = 'Enter further instructions for the amateur astronomer', widget = forms.Textarea)
