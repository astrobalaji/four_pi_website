from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import AmaOB

class AmaOnboarding(forms.ModelForm):
    obs_name = forms.CharField(label = 'Enter the name of your observatory setup',strip = True, required = True)
    location = forms.CharField(label = 'Enter your city and country of the observatory',strip = True, required = True)
    lat = forms.FloatField(label = 'Latitude (decimals)', required = True, min_value = -90., max_value = 90.)
    lon = forms.FloatField(label = 'Latitude (decimals)', required = True, min_value = -180., max_value = 180.)
    tz = forms.FloatField(label = 'Time zone +/- hours in decimals from UTC', required = True, min_value = -12., max_value = 12.)
    avail = forms.BooleanField(label = 'Available for Observation', help_text = 'Would you be interested in observing scientific data?')
    telescope_aper = forms.FloatField(label = 'Telescope Aperture (mm)', required = True, min_value = 0.)
    telescope_flength = forms.FloatField(label = 'Telescope Focal Length (mm)', required = True, min_value = 0.)
    det_mod = forms.CharField(label = 'Model name of the detector/Camera', required = True)
    det_pix_scale = forms.FloatField(label = 'pixel scale of the detector (microns)', min_value = 0., required = True)
    detector_dimensions = forms.CharField(label = 'dimensions of the detector pixels (# of pixels)', help_text = 'required format: 0000x0000 pixels', required = True)

    class Meta:
        model = AmaOB
        exclude = ['user_id', 'fov']

    ## Check for the detector dimensions data
    def clean_det_dim(self):
        data = self.cleaned_data['detector_dimensions']
        data = data.lower()
        strpd_data = data.split('x')

        ## Check if the data has been entered in the right format
        if len(strpd_data) != 2:
            raise ValidationError(_('Wrong dimensions (please check the values)'))

        ## Check if the data has two integer detector_dimensions
        if (not strpd_data[0].isdigit()) and (not strpd_data[1].isdigit()):
            raise ValidationError(_('Dimensions are not numeric.'))

        return data
