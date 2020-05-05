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
            context = {'form':form, 'edit':False}
            return render(request, 'obsprop.html', context)
        else:
            return redirect('https://4pi-astro.com/accounts/login')

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            obs_req = form.save(commit=False)
            uname = request.user.username
            obs_req.user_id = uname
            obs_req.status = 'Submitted'
            obs_req.selected_users = ''
            obs_req.save()
            return redirect('/obs_sel/'+str(obs_req.pk))
        else:
            return render(request, 'obsprop.html', {'form':form, 'edit':False})

class ObsPropEdit(View):
    form_class = ObsProp

    def get(self, request, pk, *args, **kwargs):


        if request.user.is_authenticated:
            fname = request.user.first_name
            lname = request.user.last_name
            full_name = fname+' '+lname
            data = Obs_Prop.objects.filter(pk=pk).values()[0]
            exclude_keys = ['user_id', 'status', 'submitted_on', 'selected_users', 'unselected_users', 'requested_users', 'accepted_users', 'completed_users', 'rejected_users', 'settings', 'exps']
            for k in exclude_keys:
                del data[k]
            form = self.form_class(initial = data)
            context = {'form':form, 'edit':True}
            return render(request, 'obsprop.html', context)
        else:
            return redirect('https://4pi-astro.com/accounts/login')

    def post(self, request, pk, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            obs_req = form.save(commit=False)
            obs_pk = pk
            uname = request.user.username
            obs_req.user_id = uname
            obs_req.status = 'Submitted'
            obs_req.selected_users = ''
            obs_req.save()
            return redirect('/obs_sel/'+str(obs_req.pk))
        else:
            return redirect('/obsprop/edit/{0}'.format(pk))
