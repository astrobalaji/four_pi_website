from django.shortcuts import render
from obs_propose.models import Obs_Prop
from amateurOnboarding.models import AmaOB
from django.views.generic import View
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
        context['fov'] = proposal.fov
        context['mag'] = proposal.magnitude
        context['des_exp'] = 'min: '+str(proposal.exp_min)+'s'+' max: '+str(proposal.exp_max)
        context['description'] = proposal.description
        context['settings'] = proposal.settings
        context['obs_id'] = proposal.pk

        sel_users = proposal.selected_users.split(',')
        obs_data = []
        for u in sel_users:
            obj = AmaOB.objects.filter(user_id=u)
            obs = next(obj.iterator())
            ob_data = {}
            ob_data['obs_name'] = obs.obs_name
            ob_data['location'] = obs.location
            ob_data['aper'] = obs.telescope_aper
            ob_data['flen'] = obs.telescope_flength
            ob_data['det'] = obs.det_mod
            ob_data['fov'] = "{:.2f}".format(obs.fov/60.)
            ob_data['uname'] = u
            ob_data['obs_link'] = 'http://localhost:8000/obs_calc/'+u+'-'+pk
            lp = get_SQM_reading(obs.lat, obs.lon)
            if lp == 0.:
                ob_data['lp'] = 'NA'
            else:
                ob_data['lp'] = str("{:.2f}".format(lp))
            obs_data.append(ob_data)
        context['observatories'] = obs_data
        return render(request, 'obs_overview_prof.html', context)

class ReqObservatory(View):
    def get(self, request, slug, pk, *args, **kwargs):
        obj = Obs_Prop.objects.filter(pk=pk)
        proposal = next(obj.iterator())
        if proposal.requested_users == '':
            proposal.requested_users = slug
        else:
            req_users = proposal.requested_users.split(',')
            req_users.append(slug)
            proposal.requested_users = ','.join(req_users)
        proposal.status = 'Requested'
        proposal.save()
        return render(request, 'autoclose.html')
