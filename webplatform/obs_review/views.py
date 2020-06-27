from django.shortcuts import render, redirect
from django.views.generic import View
from .models import obs_rev
from .forms import obs_rev_form
from obs_propose.models import Obs_Prop
from amateurOnboarding.models import AmaOB

# Create your views here.
class review_view(View):
    form_class = obs_rev_form

    def get(self, request, slug, pk, *args, **kwargs):
        if request.user.is_authenticated:
            obs_data = next(Obs_Prop.objects.filter(pk = pk).iterator())
            if obs_data.user_id == request.user.username:

                form = self.form_class()
                observatory_data = next(AmaOB.objects.filter(user_id = slug).iterator())
                obsprop = next(Obs_Prop.objects.filter(pk = pk).iterator())
                context = {'form':form, 'obser_title': observatory_data.obs_name, 'prop_title': obsprop.obs_title}
                return render(request, 'review.html', context)
            else:
                return redirect('/user/home')
        else:
            return redirect('accounts/login')

    def post(self, request, slug, pk, *args, **kwargs):
        form = self.form_class(request.POST)
        observatory_data = next(AmaOB.objects.filter(user_id = slug).iterator())
        obsprop = next(Obs_Prop.objects.filter(pk = pk).iterator())
        if form.is_valid():
            obs_rev = form.save(commit=False)
            uname = request.user.username
            obs_rev.obs_id = slug
            obs_rev.prop_pk = pk
            obs_rev.obs_title = observatory_data.obs_name
            obs_rev.prop_title = obsprop.obs_title
            obs_rev.save()
            context = {'obs_pk':pk}
            return render(request, 'thank_you.html', context)
