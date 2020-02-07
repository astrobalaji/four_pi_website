from django.shortcuts import render

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        fname = request.user.first_name
        lname = request.user.last_name
        full_name = fname+' '+lname
        return render(request, 'user_home.html', {'full_name':full_name})
