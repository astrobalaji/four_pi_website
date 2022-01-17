from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class ObsDatePick(forms.Form):
    start_date = forms.DateField(label = 'Starting date of the observation', required = False, widget=forms.SelectDateWidget(attrs = {'style':'width:30%', 'cols':3}))
    no_of_nights = forms.IntegerField(label = 'Number of nights', required = False, widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
