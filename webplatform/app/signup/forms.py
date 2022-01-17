from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

# Sign Up Form
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, widget = forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    last_name = forms.CharField(max_length=30, required=False, widget = forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    email = forms.EmailField(max_length=254, help_text='Enter a valid email address', widget = forms.TextInput(attrs={'style': 'width: 30%', 'cols': 200,'rows': 1}))
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            #'user_dir'
            ]
