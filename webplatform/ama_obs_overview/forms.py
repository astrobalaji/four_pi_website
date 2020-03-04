from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import FileUpload

class File_Upload(forms.ModelForm):
    data = forms.FileField(label = 'Data files')
    #obs_comments = forms.CharField(widget = forms.Textarea, label = 'Comments')
    class Meta:
        model = FileUpload
        fields = ['data']
