from django.shortcuts import render
from django.views.generic import View

# Create your views here.
class eduOBViews(View):

    def get(self, request):
        if request.user.is_authenticated:
            fname = request.user.first_name
            lname = request.user.last_name
            full_name = fname+' '+lname
            context = {'full_name':full_name}
            return render(request, 'Onboarding/eduOb.html', context)
