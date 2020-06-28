from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import obs_rev
from django_starfield import Stars

class obs_rev_form(forms.ModelForm):
    #obs_title = forms.CharField(max_length=200)
    #prop_title = forms.CharField(max_length=200)
    snr = forms.IntegerField(label = 'Signal-to-noise Ratio', widget = Stars(stars=10), help_text = 'How do you rate the SNR of the data?')
    accuracy = forms.IntegerField(label = 'Tracking accuracy', widget = Stars(stars=10), help_text='How do you rate the PSF of the data?')
    quality_calib = forms.IntegerField(label = 'Quality of Calibration data', widget = Stars(stars=10), help_text = 'How do you rate the quality of the calibration data  (e.g. Dark, Flat-Field data etc.)?')
    instructs_follow = forms.IntegerField(label = 'Following the instructions', widget = Stars(stars=10), help_text ="How do you rate the observer's instruction following ability?")
    title = forms.CharField(label = 'Title of the Review')
    review = forms.CharField(widget = forms.Textarea(attrs={'style': 'width: 100%'}), label = 'Write your review')
    class Meta:
        model = obs_rev
        exclude =  ['obs_title', 'posted_at', 'prop_title', 'prop_pk', 'obs_id']
