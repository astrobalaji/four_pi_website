from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Obs_Prop

type_choices = [('r','Regular'), ('sos','SOS')]
field_choices = [('s', 'Single Object'), ('m', 'Multiple Object/Crowded Field'), ('chance', 'Chance of Discovery')]

class ObsProp(forms.ModelForm):

    obs_title = forms.CharField(label = 'Enter a title for your observation', required = True)
    obs_type = forms.ChoiceField(choices = type_choices, required = True)
    field_type = forms.ChoiceField(choices = field_choices, required = True)
    coords_ra = forms.CharField(label = 'RA of the target/center of field in decimals (00h00m00s)', required = True)
    coords_dec = forms.CharField(label = 'Dec of the target/center of field in decimals (00d00m00s)', required = True)
    fov = forms.FloatField(label = 'Desired minimum field of view in arc_minutes', required = True)
    magnitude = forms.FloatField(label = 'Expected V band magnitude of the Object', required = True)
    start_date = forms.DateField(label = 'Enter your start date', required = True, widget = forms.SelectDateWidget)
    no_of_nights = forms.IntegerField(label = 'Number of nights', required = True)
    exp_min = forms.FloatField(label = 'Desired Minimum Exposure (seconds)', required = True)
    exp_max = forms.FloatField(label = 'Desired Maximum Exposure (seconds)', required = True)
    #desired_exposure = forms.FloatField(label = 'Desired Exposure time in seconds', required = True)
    description = forms.CharField(widget = forms.Textarea, label = 'A brief description of your science case', required = True)
    #settings = forms.CharField(widget = forms.Textarea, label = 'Any further instructions for the Observer')

    class Meta:
        model = Obs_Prop
        exclude = ['user_id', 'status', 'submitted_on', 'selected_users', 'unselected_users', 'requested_users', 'accepted_users', 'completed_users', 'settings', 'exps']
