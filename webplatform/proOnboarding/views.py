from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import proOnboard
from django.views.generic import View
import numpy as np
from .models import proOB
# Create your views here.

class proOBViews(View):
    form_class = proOnboard

    def get(self, request):
        form = self.form_class()

        if request.user.is_authenticated:
            fname = request.user.first_name
            lname = request.user.last_name
            full_name = fname+' '+lname
            context = {'form':form, 'full_name':full_name}
            return render(request, 'Onboarding/proOb.html', context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            pro_user = form.save(commit=False)
            uname = request.user.username
            pro_user.user_id = uname
            pro_user.save()
            return redirect('/user/home/')
