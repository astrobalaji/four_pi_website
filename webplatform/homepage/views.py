from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
# Create your views here.
def index(request):
    return render_to_response('landingpage.html')
