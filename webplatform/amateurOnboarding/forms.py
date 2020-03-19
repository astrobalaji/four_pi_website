from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import AmaOB

class AmaOnboarding(forms.ModelForm):
    obs_name = forms.CharField(label = 'Name of your observatory (*)',strip = True, required = True, help_text = 'Give any name to your setup. You can be creative ;)', widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    location = forms.CharField(label = 'City and Country of the observatory (*)',strip = True, required = True, help_text = 'Format: City, Country', widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    lat = forms.FloatField(label = 'Latitude (decimals) (*)', required = True, min_value = -90., max_value = 90., help_text = 'Use negative values for Southern hemisphere.',widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    lon = forms.FloatField(label = 'Longitude (decimals) (*)', required = True, min_value = -180., max_value = 180., help_text = 'Use negative values for Western hemisphere', widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    tz = forms.FloatField(label = 'Time zone +/- hours in decimals from UTC (*)', help_text = 'UTC: Coordinated Universal Time (GMT)' , required = True, min_value = -12., max_value = 12., widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    obs_img = forms.ImageField(label = 'Upload a picture of your observatory (*)', required = True, help_text = 'Preferrably in jpg/jpeg format', widget=forms.FileInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    telescope_mod = forms.CharField(label=' Manufacturer / Model of the telescope (*)', required = True, widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    telescope_aper = forms.FloatField(label = 'Telescope Aperture (mm) (*)', required = True, min_value = 0., widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    telescope_flength = forms.FloatField(label = 'Telescope Effective Focal Length (mm) (*)', required = True, min_value = 0., help_text = "Factor in for focal reducers (if any)", widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    det_mod = forms.CharField(label = 'Model/ Name of the detector/ camera (*)', required = True, widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    chip_name = forms.CharField(label = 'Manufacturer / Model of the detector chip', required = False, help_text='Optional but highly desired', widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    det_pix_scale = forms.FloatField(label = 'Physical pixel size of the detector (microns) (*)', min_value = 0., required = True, help_text = 'Average if pixel is not a square', widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    detector_dimensions = forms.CharField(label = 'Dimensions of the detector (# of pixels) (*)', help_text = 'Required format: 0000x0000 pixels', required = True, widget=forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    read_noise = forms.FloatField(label = 'Read Noise of the Detector (in electrons)',min_value = 0., help_text='Optional but highly desired', required = False, widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    QE = forms.FloatField(label = 'Quantum Efficiency of the detector (in %)', min_value = 0., max_value = 100., help_text = 'Optional but highly desired', required = False, widget=forms.NumberInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    class Meta:
        model = AmaOB
        exclude = ['user_id', 'fov', 'credits', 'total_credits', 'booked_dates', 'SQM']
