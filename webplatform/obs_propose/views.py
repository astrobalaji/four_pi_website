from django.shortcuts import render, redirect
from .forms import ObsProp
from django.views.generic import View
import numpy as np
from .models import Obs_Prop
from datetime import date
# Create your views here.


class ObsPropViews(View):
    form_class = ObsProp

    def get(self, request):
        form = self.form_class()

        if request.user.is_authenticated:
            fname = request.user.first_name
            lname = request.user.last_name
            full_name = fname+' '+lname
            context = {'form':form}
            return render(request, 'obsprop.html', context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            obs_req = form.save(commit=False)
            uname = request.user.username
            obs_req.user_id = uname
            obs_req.status = 'Submitted'
            obs_req.selected_users = ''
            obs_req.save()
            return redirect('/obs_sel')
        else:
            return redirect('/obsprop')
