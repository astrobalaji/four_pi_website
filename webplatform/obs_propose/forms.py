from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Obs_Prop
from bootstrap_datepicker_plus import DatePickerInput

type_choices = [('r','Regular'), ('sos','High Priority')]
field_choices = [('s', 'Single Object'), ('m', 'Crowded Field')]#, ('chance', 'Chance of Discovery')]

class ObsProp(forms.ModelForm):

    obs_title = forms.CharField(label = 'Enter a title for your observation', required = True, widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    obs_type = forms.ChoiceField(choices = type_choices, required = True, widget=forms.Select(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    field_type = forms.ChoiceField(choices = field_choices, required = True, widget=forms.Select(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    coords_ra = forms.CharField(label = 'RA of the target/center of field', required = True, help_text = 'format: 00h00m00.00s', widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    coords_dec = forms.CharField(label = 'Dec of the target/center of field', required = True, help_text = 'format: 00d00m00.00s', widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    min_fov = forms.FloatField(label = 'Desired Minimum field of view (arcminutes)', required = True, widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    max_fov = forms.FloatField(label = 'Desired Maximum field of view (arcminutes)', required = True, widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    magnitude = forms.FloatField(label = 'Expected V band magnitude of the object', required = True, help_text='AGNs: Approximate magnitude for an aperture of ~1-3 arcseconds', widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    start_date = forms.DateField(label = 'Start date of the observation', required = True, widget = DatePickerInput(attrs = {'stype':'width:30%', 'cols':20}))#forms.SelectDateWidget(attrs = {'style':'width:30%', 'cols':3}))
    no_of_nights = forms.IntegerField(label = 'Number of nights', required = True, widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    #exp_min = forms.FloatField(label = 'Desired Minimum Integrated Exposure (seconds)', required = True, help_text = 'Used in the SNR calculation', widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    #exp_max = forms.FloatField(label = 'Desired Maximum Integrated Exposure (seconds)', required = True, help_text = 'Used in the SNR calculation', widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    min_snr = forms.FloatField(label = 'Desired SNR', required = True, help_text = 'Minimum value of 10', min_value = 10., widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    description = forms.CharField(widget = forms.Textarea(attrs={'style': 'width: 50%'}), label = 'A brief description of the science case', required = True)

    class Meta:
        model = Obs_Prop
        exclude = ['user_id', 'status', 'submitted_on', 'selected_users', 'unselected_users', 'requested_users', 'accepted_users', 'completed_users', 'rejected_users', 'settings', 'exps']
