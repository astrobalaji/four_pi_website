from django.shortcuts import render, redirect
from obs_propose.models import Obs_Prop
from amateurOnboarding.models import AmaOB
from django.views.generic import View
from ama_obs_overview.models import File_Details
from django.core.files import File

import mimetypes
import pandas as pd
from math import sin, cos, sqrt, atan2



lp_df = pd.read_csv('datafiles/LP_data.csv')

obs_choices = {'r':'Regular', 'sos':'SOS'}
field_choices = {'s': 'Single Object', 'm': 'Multiple Object/Crowded Field', 'chance': 'Chance of Discovery'}

def dist(row,lat, lon):
    R = 6373.0


    dlon = row['Longitude'] - lon
    dlat = row['Latitude'] - lat
    a = (sin(dlat/2))**2 + cos(row['Latitude']) * cos(lat) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def get_SQM_reading(lat, lon):
    lp_df['distance'] = lp_df.apply(lambda x: dist(x, lat, lon), axis = 1)
    lp_df_sel = lp_df[lp_df['distance']<=100.]
    if len(lp_df_sel) != 0:
        return lp_df_sel['SQM Reading'].mean()
    else:
        return 0.


class Obs_Overview_views(View):
    def get(self, request, pk, *args, **kwargs):
        obj = Obs_Prop.objects.filter(pk=pk)
        proposal = next(obj.iterator())
        context = {}
        context['obs_title'] = proposal.obs_title
        context['obs_type'] = obs_choices[proposal.obs_type]
        context['field_type'] = field_choices[proposal.field_type]
        context['coords_ra'] = proposal.coords_ra
        context['coords_dec'] = proposal.coords_dec
        context['min_fov'] = proposal.min_fov
        context['max_fov'] = proposal.min_fov
        context['mag'] = proposal.magnitude
        context['des_exp'] = 'min: '+str(proposal.exp_min)+'s'+' max: '+str(proposal.exp_max)
        context['description'] = proposal.description
        context['settings'] = proposal.settings
        context['obs_id'] = proposal.pk
        acc_users = proposal.accepted_users.split(',')
        comp_users = proposal.completed_users.split(',')
        req_users = proposal.requested_users.split(',')

        sel_users = proposal.selected_users.split(',')
        obs_data = []
        if sel_users == ['']:
            return redirect('http://localhost:8000/obs_sel/'+str(pk))
        else:
            for u in sel_users:
                obj = AmaOB.objects.filter(user_id=u)
                obs = next(obj.iterator())
                ob_data = {}
                if u in comp_users:
                    ob_data['comp'] = True
                    ob_data['req'] = False
                    data_download = next(File_Details.objects.filter(obs_id=pk, ama_id=u).iterator())
                    #ob_data['data'] = data_download.filename
                    some_file  = open('media/data_files/'+data_download.filename, "r")
                    django_file = File(some_file)
                    ob_data['data'] = django_file
                else:
                    ob_data['comp'] = False
                    ob_data['req'] = True
                if u in req_users:
                    obs_status = 'Requested'
                elif u in acc_users:
                    obs_status = 'Accepted'
                elif u in comp_users:
                    obs_status = 'Completed'
                else:
                    obs_status = 'Selected'
                ob_data['obs_name'] = obs.obs_name
                ob_data['location'] = obs.location
                ob_data['aper'] = obs.telescope_aper
                ob_data['flen'] = obs.telescope_flength
                ob_data['det'] = obs.det_mod
                ob_data['fov'] = "{:.2f}".format(obs.fov)
                ob_data['uname'] = u
                ob_data['obs_img'] = obs.obs_img
                ob_data['status'] = obs_status
                ob_data['obs_link'] = 'https://4pi-astro.com/obs_calc/'+u+'-'+pk
                lp = get_SQM_reading(obs.lat, obs.lon)
                if lp == 0.:
                    ob_data['lp'] = 'NA'
                else:
                    ob_data['lp'] = str("{:.2f}".format(lp))
                obs_data.append(ob_data)
            context['observatories'] = obs_data
            return render(request, 'obs_overview_prof.html', context)
