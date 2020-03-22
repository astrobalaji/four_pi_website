from django.shortcuts import render, redirect
from django.views.generic import View
from obs_propose.models import Obs_Prop
from amateurOnboarding.models import AmaOB
from ast import literal_eval
from datetime import datetime, timedelta
from .forms import File_Upload
from .models import FileUpload, File_Details
import os
import shutil
import zipfile
import subprocess
import sys
from background_task import background

from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import send_mail


obs_choices = {'r':'Regular', 'sos':'SOS'}
field_choices = {'s': 'Single Object', 'm': 'Multiple Object/Crowded Field', 'chance': 'Chance of Discovery'}


def send_acc_email(ama_uname,prof_uname,  obs_title, obs_pk):
    prof_obj = next(User.objects.filter(username=prof_uname).iterator())
    obs_obj = next(AmaOB.objects.filter(user_id = ama_uname).iterator())
    fname = prof_obj.first_name
    lname = prof_obj.last_name
    full_name = fname+' '+lname
    obs_name = obs_obj.obs_name
    subject = '{0} has accepted your obsevation request'.format(obs_name)
    message = render_to_string('emails/accept_email.html', {
        'user_fname': full_name,
        'obs_name': obs_name,
        'obs_title': obs_title,
        'obs_id': obs_pk,
        'ama_id':ama_uname
    })
    send_mail(subject = subject, message = message, from_email = 'astrobot@4pi-astro.com', recipient_list = [prof_obj.email])

def send_rej_email(ama_uname,prof_uname,  obs_title, obs_pk):
    prof_obj = next(User.objects.filter(username=prof_uname).iterator())
    obs_obj = next(AmaOB.objects.filter(user_id = ama_uname).iterator())
    fname = prof_obj.first_name
    lname = prof_obj.last_name
    full_name = fname+' '+lname
    obs_name = obs_obj.obs_name
    subject = '{0} has rejected your obsevation request'.format(obs_name)
    message = render_to_string('emails/reject_email.html', {
        'user_fname': full_name,
        'obs_name': obs_name,
        'obs_title': obs_title,
        'obs_id': obs_pk,
    })
    send_mail(subject = subject, message = message, from_email = 'astrobot@4pi-astro.com', recipient_list = [prof_obj.email])


# Create your views here.
class ama_overview_views(View):
    form_class = File_Upload
    def get(self, request, pk, *args, **kwargs):
        res = Obs_Prop.objects.filter(pk=pk).iterator()
        Proposal = next(res)
        prop_data = {}
        prop_data['title'] = Proposal.obs_title
        prop_data['description'] = Proposal.description
        prop_data['obs_type'] = obs_choices[Proposal.obs_type]
        prop_data['field_type'] = field_choices[Proposal.field_type]
        prop_data['min_fov'] = Proposal.min_fov
        prop_data['max_fov'] = Proposal.max_fov
        prop_data['mag'] = Proposal.magnitude
        prop_data['ra'] = Proposal.coords_ra
        prop_data['dec'] = Proposal.coords_dec
        prop_data['settings'] = literal_eval(Proposal.settings)[request.user.username]
        prop_data['req_users'] = Proposal.requested_users
        prop_data['accepted_users'] = Proposal.accepted_users
        prop_data['exps'] = literal_eval(Proposal.exps)[request.user.username]

        if request.user.username in prop_data['req_users']:
            req = True
        else:
            req = False
        if request.user.username in prop_data['accepted_users']:
            accept = True
        else:
            accept = False

        prop_data['requested'] = req
        prop_data['accepted'] = accept

        prop_data['pk'] = pk
        prop_data['uname'] = request.user.username

        if accept:
            form = self.form_class()
            prop_data['form'] = form
        return render(request, 'obs_overview_ama.html', prop_data)
    def post(self, request, pk, *args, **kwargs):
        data = next(Obs_Prop.objects.filter(pk=pk).iterator())
        form = self.form_class(request.POST, request.FILES)
        filename = request.FILES['data']
        file_det = File_Details(prof_id = data.user_id,
                                ama_id = request.user.username,
                                obs_id = pk,
                                filename = filename)
        if data.completed_users == '':
            data.completed_users = request.user.username
        else:
            comp_users = data.completed_users.split(',')
            comp_users.append(request.user.username)
            data.completed_users = ','.join(comp_users)
        acc_users = data.accepted_users.split(',')
        acc_users.remove(request.user.username)
        data.accepted_users = ','.join(acc_users)
        data.save()
        form.save()
        file_det.save()
        extract_files(pk, request.user.username, filename.name)
        return redirect('/user/home')

class accept_obs(View):
    def get(self, request, slug, pk, *args, **kwargs):
        res = Obs_Prop.objects.filter(pk=pk).iterator()
        user_res = next(AmaOB.objects.filter(user_id=slug).iterator())
        Proposal = next(res)
        req_users = Proposal.requested_users.split(',')
        if len(req_users)!=1:
            req_users.remove(slug)
            Proposal.requested_users = ','.join(req_users)
        else:
            Proposal.requested_users = ''
        if Proposal.accepted_users == '':
            Proposal.accepted_users = slug
        else:
            acc_users = Proposal.accepted_users.split(',')
            acc_users.append(slug)
            acc_users = list(set(acc_users))
            Proposal.accepted_users = ','.join(acc_users)
        Proposal.save()

        start_date = Proposal.start_date
        days = []
        for i in range(Proposal.no_of_nights):
            temp_date = start_date+timedelta(days=i)
            days.append(temp_date.strftime('%Y-%m-%d'))

        if user_res.booked_dates == '':
            user_res.booked_dates = ','.join(days)
        else:
            booked_dates = user_res.booked_dates.split(',')
            booked_dates += days
            user_res.booked_dates = ','.join(booked_dates)
        user_res.save()
        send_acc_email(slug, Proposal.user_id,  Proposal.obs_title, pk)
        render(request, 'autoclose.html')
        return redirect('https://4pi-astro.com/user/home')

class reject_obs(View):
    def get(self, request, slug, pk, *args, **kwargs):
        res = Obs_Prop.objects.filter(pk=pk).iterator()
        Proposal = next(res)
        req_users = Proposal.requested_users.split(',')
        if len(req_users)!=1:
            req_users.remove(slug)
            Proposal.requested_users = ','.join(req_users)
        else:
            Proposal.requested_users = ''
        if Proposal.rejected_users == '':
            Proposal.rejected_users = slug
        else:
            rej_users = Proposal.rejected_users.split(',')
            rej_users.append(slug)
            rej_users = list(set(rej_users))
            Proposal.rejected_users = ','.join(rej_users)
            Proposal.save()
        send_rej_email(slug, Proposal.user_id,  Proposal.obs_title, pk)
        return render(request, 'autoclose.html')


@background(schedule=1)
def extract_files(pk, ama_id, filename):
    base_path = 'media/data_files/'
    if not os.path.exists(base_path+pk):
        os.mkdir(base_path+pk)

    if not os.path.exists(base_path+pk+'/'+ama_id):
        os.mkdir(base_path+pk+'/'+ama_id)

    shutil.move(base_path+filename, base_path+pk+'/'+ama_id+'/'+filename)

    with zipfile.ZipFile(base_path+pk+'/'+ama_id+'/'+filename, 'r') as zip_ref:
         zip_ref.extractall(base_path+pk+'/'+ama_id+'/')

    cr2check = [f for f in os.listdir(base_path+pk+'/'+ama_id+'/lights/') if (f.endswith('.CR2')) or (f.endswith('.cr2'))]

    if len(cr2check)!=0:
        cr2 = 1
    else:
        cr2 = 0

    if cr2==1:

        os.mkdir(base_path+pk+'/'+ama_id+'fits_files')
        os.mkdir(base_path+pk+'/'+ama_id+'fits_files/lights')
        os.mkdir(base_path+pk+'/'+ama_id+'fits_files/darks')
        os.mkdir(base_path+pk+'/'+ama_id+'fits_files/bias')
        os.mkdir(base_path+pk+'/'+ama_id+'fits_files/flats')



        lights_files = os.listdir(base_path+pk+'/'+ama_id+'/lights/')
        darks_files = os.listdir(base_path+pk+'/'+ama_id+'/darks/')
        bias_files = os.listdir(base_path+pk+'/'+ama_id+'/bias/')
        flats_files = os.listdir(base_path+pk+'/'+ama_id+'/flats/')

        for f in lights_files:
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/lights/'+f, '0'])
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/lights/'+f, '1'])
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/lights/'+f, '2'])

        lights_fits = [f for f in os.listdir(base_path+pk+'/'+ama_id+'/lights/') if f.endswith('.fits')]


        for f in lights_fits:
            data = fits.open(base_path+pk+'/'+ama_id+'/lights/'+f)
            head = data[0].header
            exposure = head['EXPTIME'].replace(' ', '').replace('/', '&')
            filt = head['FILTER'].replace(' ', '')
            if not os.path.exists(base_path+pk+'/'+ama_id+'/fits_files/lights/'+exposure):
                os.mkdir(base_path+pk+'/'+ama_id+'/fits_files/lights/'+exposure)
                #os.mkdir('fits_files/lights/'+exposure+'/'+filt)
            if not os.path.exists(base_path+pk+'/'+ama_id+'/fits_files/lights/'+exposure+'/'+filt):
                os.mkdir(base_path+pk+'/'+ama_id+'/fits_files/lights/'+exposure+'/'+filt)
            shutil.move(base_path+pk+'/'+ama_id+'/lights/'+f, base_path+pk+'/'+ama_id+'/fits_files/lights/'+exposure+'/'+filt+'/')


        for f in tqdm(darks_files):
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/darks/'+f, '0'])
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/darks/'+f, '1'])
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/darks/'+f, '2'])

        darks_fits = [f for f in os.listdir(base_path+pk+'/'+ama_id+'/darks/') if f.endswith('.fits')]


        for f in darks_fits:
            data = fits.open(base_path+pk+'/'+ama_id+'/darks/'+f)
            head = data[0].header
            exposure = head['EXPTIME'].replace(' ', '').replace('/', '&')
            filt = head['FILTER'].replace(' ', '')
            if not os.path.exists(base_path+pk+'/'+ama_id+'/fits_files/darks/'+exposure):
                os.mkdir(base_path+pk+'/'+ama_id+'/fits_files/darks/'+exposure)
                #os.mkdir('fits_files/darks/'+exposure+'/'+filt)
            if not os.path.exists(base_path+pk+'/'+ama_id+'/fits_files/darks/'+exposure+'/'+filt):
                os.mkdir(base_path+pk+'/'+ama_id+'/fits_files/darks/'+exposure+'/'+filt)
            shutil.move(base_path+pk+'/'+ama_id+'/darks/'+f, base_path+pk+'/'+ama_id+'/fits_files/darks/'+exposure+'/'+filt+'/')


        for f in flats_files:
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/flats/'+f, '0'])
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/flats/'+f, '1'])
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/flats/'+f, '2'])

        flats_fits = [f for f in os.listdir(base_path+pk+'/'+ama_id+'/flats/') if f.endswith('.fits')]


        for f in flats_fits:
            data = fits.open(base_path+pk+'/'+ama_id+'/flats/'+f)
            head = data[0].header
            exposure = head['EXPTIME'].replace(' ', '').replace('/', '&')
            filt = head['FILTER'].replace(' ', '')
            if not os.path.exists(base_path+pk+'/'+ama_id+'/fits_files/flats/'+exposure):
                os.mkdir(base_path+pk+'/'+ama_id+'/fits_files/flats/'+exposure)
                #os.mkdir('fits_files/flats/'+exposure+'/'+filt)
            if not os.path.exists(base_path+pk+'/'+ama_id+'/fits_files/flats/'+exposure+'/'+filt):
                os.mkdir(base_path+pk+'/'+ama_id+'/fits_files/flats/'+exposure+'/'+filt)
            shutil.move(base_path+pk+'/'+ama_id+'/flats/'+f, base_path+pk+'/'+ama_id+'/fits_files/flats/'+exposure+'/'+filt+'/')


        for f in bias_files:
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/bias/'+f, '0'])
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/bias/'+f, '1'])
            sp.call(['python', 'aux_scripts/cr2fits/cr2fits.py', base_path+pk+'/'+ama_id+'/bias/'+f, '2'])

        bias_fits = [f for f in os.listdir(base_path+pk+'/'+ama_id+'/bias/') if f.endswith('.fits')]


        for f in bias_fits:
            data = fits.open(base_path+pk+'/'+ama_id+'/bias/'+f)
            head = data[0].header
            exposure = head['EXPTIME'].replace(' ', '').replace('/', '&')
            filt = head['FILTER'].replace(' ', '')
            if not os.path.exists(base_path+pk+'/'+ama_id+'/fits_files/bias/'+exposure):
                os.mkdir(base_path+pk+'/'+ama_id+'/fits_files/bias/'+exposure)
                #os.mkdir('fits_files/bias/'+exposure+'/'+filt)
            if not os.path.exists(base_path+pk+'/'+ama_id+'/fits_files/bias/'+exposure+'/'+filt):
                os.mkdir(base_path+pk+'/'+ama_id+'/fits_files/bias/'+exposure+'/'+filt)
            shutil.move(base_path+pk+'/'+ama_id+'/bias/'+f, base_path+pk+'/'+ama_id+'/fits_files/bias/'+exposure+'/'+filt+'/')
