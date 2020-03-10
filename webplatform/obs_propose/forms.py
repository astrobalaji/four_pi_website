from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Obs_Prop

type_choices = [('r','Regular'), ('sos','High Priority')]
field_choices = [('s', 'Single Object'), ('m', 'Crowded Field')]#, ('chance', 'Chance of Discovery')]

class ObsProp(forms.ModelForm):

    obs_title = forms.CharField(label = 'Enter a title for your observation', required = True)
    obs_type = forms.ChoiceField(choices = type_choices, required = True)
    field_type = forms.ChoiceField(choices = field_choices, required = True)
    coords_ra = forms.CharField(label = 'RA of the target/center of field', required = True, help_text = 'format: 00h00m00.00s')
    coords_dec = forms.CharField(label = 'Dec of the target/center of field', required = True, help_text = 'format: 00d00m00.00s')
    min_fov = forms.FloatField(label = 'Desired Minimum field of view (arcminutes)', required = True)
    max_fov = forms.FloatField(label = 'Desired Maximum field of view (arcminutes)', required = True)
    magnitude = forms.FloatField(label = 'Expected V band magnitude of the object', required = True, help_text='AGNs: Prefer a magnitude with aperture close to 1-3 arcseconds')
    start_date = forms.DateField(label = 'Enter the start date of the observation', required = True, widget = forms.SelectDateWidget)
    no_of_nights = forms.IntegerField(label = 'Number of nights', required = True)
    exp_min = forms.FloatField(label = 'Desired Minimum Integrated Exposure (seconds)', required = True, help_text = 'Used in the SNR calculation')
    exp_max = forms.FloatField(label = 'Desired Maximum Integrated Exposure (seconds)', required = True, help_text = 'Used in the SNR calculation')
    description = forms.CharField(widget = forms.Textarea, label = 'A brief description of the science case', required = True)

    class Meta:
        model = Obs_Prop
        exclude = ['user_id', 'status', 'submitted_on', 'selected_users', 'unselected_users', 'requested_users', 'accepted_users', 'completed_users', 'settings', 'exps']
