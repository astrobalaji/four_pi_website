from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
# Create your views here.
def index(request):
    if request.user.username == 'copernicus':
        return render_to_response('landingpage.html')
    else:
        return redirect('/user/home')
