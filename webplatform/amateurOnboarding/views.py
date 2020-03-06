from django.shortcuts import render, redirect
from .forms import AmaOnboarding
from django.views.generic import View
import numpy as np
from .models import AmaOB
# Create your views here.

def calc_fov(flen, pixscale, dims):
    dims = [int(x) for x in dims.split('x')]
    arc_per_pix = 200.*pixscale/flen
    return np.sqrt((dims[0]**2.)+(dims[1]**2.))*arc_per_pix/60.

class AmaOBViews(View):
    form_class = AmaOnboarding

    def get(self, request):
        form = self.form_class()

        if request.user.is_authenticated:
            fname = request.user.first_name
            lname = request.user.last_name
            full_name = fname+' '+lname
            context = {'form':form, 'full_name':full_name}
            return render(request, 'Onboarding/AmaOb.html', context)

    def post(self, request):
        form = self.form_class(request.POST ,request.FILES)
        if form.is_valid():
            observatory = form.save(commit=False)
            uname = request.user.username
            observatory.user_id = uname
            fov = calc_fov(observatory.telescope_flength, observatory.det_pix_scale, observatory.detector_dimensions)
            observatory.fov = fov
            observatory.save()
            return redirect('/user/home/')
        else:
            return redirect('/onboarding/amateur')
