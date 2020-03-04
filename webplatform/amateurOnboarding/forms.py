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
    obs_img = forms.ImageField(label = 'Upload a picture of your setup (preferrably a jpg)', required = True)
    telescope_mod = forms.CharField(label=' Manufacturer / Model of the telescope', required = True)
    telescope_aper = forms.FloatField(label = 'Telescope Aperture (mm)', required = True, min_value = 0.)
    telescope_flength = forms.FloatField(label = 'Telescope Focal Length (mm)', required = True, min_value = 0.)
    det_mod = forms.CharField(label = 'Model name of the detector/Camera', required = True)
    chip_name = forms.CharField(label = 'Manufacturer / Model of the detector chip', required = False, help_text='optional but highly desired')
    det_pix_scale = forms.FloatField(label = 'Physical pixel size of the detector (microns)', min_value = 0., required = True, help_text = 'average if pixel is not a square')
    detector_dimensions = forms.CharField(label = 'dimensions of the detector pixels (# of pixels)', help_text = 'required format: 0000x0000 pixels', required = True)
    read_noise = forms.FloatField(label = 'Read Noise of the Detector (in electrons)', required = True)
    class Meta:
        model = AmaOB
        exclude = ['user_id', 'fov', 'credits', 'total_credits', 'booked_dates']
