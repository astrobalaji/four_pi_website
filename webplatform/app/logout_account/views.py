from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('/accounts/login')
