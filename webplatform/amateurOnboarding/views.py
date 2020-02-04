from django.shortcuts import render

# Create your views here.
def init_sel(request):
    if request.user.is_authenticated:
        fname = request.user.first_name
        lname = request.user.last_name
        full_name = fname+' '+lname
        return render(request, 'activation/dir_sel.html', {'full_name':full_name})
