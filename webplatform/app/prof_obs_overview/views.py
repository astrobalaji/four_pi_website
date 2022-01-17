from django.shortcuts import render, redirect
from obs_propose.models import Obs_Prop
from amateurOnboarding.models import AmaOB
from django.views.generic import View
from ama_obs_overview.models import File_Details
from django.core.files import File
from django.http import HttpResponseNotFound

from datetime import datetime, timedelta

import mimetypes




obs_choices = {'r':'Regular', 'sos':'SOS'}
field_choices = {'s': 'Single Object', 'm': 'Multiple Object/Crowded Field', 'chance': 'Chance of Discovery'}




class Obs_Overview_views(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            obj = Obs_Prop.objects.filter(pk=pk)
            proposal = next(obj.iterator())
            if request.user.username == proposal.user_id:
                context = {}
                context['obs_title'] = proposal.obs_title
                context['obs_type'] = obs_choices[proposal.obs_type]
                context['field_type'] = field_choices[proposal.field_type]
                context['coords_ra'] = proposal.coords_ra
                context['coords_dec'] = proposal.coords_dec
                context['min_fov'] = proposal.min_fov
                context['max_fov'] = proposal.max_fov
                context['mag'] = proposal.magnitude
                context['des_snr'] = proposal.min_snr#'min: '+str(proposal.exp_min)+' s'+', max: '+str(proposal.exp_max)+' s'
                context['description'] = proposal.description
                context['settings'] = proposal.settings
                context['obs_id'] = proposal.pk
                context['start_date'] = proposal.start_date
                context['end_date'] = proposal.start_date+timedelta(days = proposal.no_of_nights)
                context['obs_pk'] = pk
                acc_users = proposal.accepted_users.split(',')
                comp_users = proposal.completed_users.split(',')
                req_users = proposal.requested_users.split(',')
                rej_users = proposal.rejected_users.split(',')
                sel_users = proposal.selected_users.split(',')
                obs_data = []
                if sel_users == ['']:
                    return redirect('https://4piastro.com/obs_sel/'+str(pk))
                else:
                    for u in sel_users:
                        obj = AmaOB.objects.filter(user_id=u)
                        obs = next(obj.iterator())
                        ob_data = {}
                        if u in comp_users:
                            ob_data['comp'] = True
                            ob_data['req'] = False
                            ob_data['not_rej'] = True
                            data_download = next(File_Details.objects.filter(obs_id=pk, ama_id=u).iterator())
                            #ob_data['data'] = data_download.filename
                            some_file  = open('media/data_files/'+data_download.filename, "r")
                            django_file = File(some_file)
                            ob_data['data'] = django_file
                        elif u in rej_users:
                            ob_data['comp'] = False
                            ob_data['req'] = True
                            ob_data['not_rej'] = False
                        else:
                            ob_data['comp'] = False
                            ob_data['req'] = True
                            ob_data['not_rej'] = True
                        if u in req_users:
                            obs_status = 'Requested'
                        elif u in acc_users:
                            obs_status = 'Accepted'
                        elif u in comp_users:
                            obs_status = 'Completed'
                        elif u in rej_users:
                            obs_status = 'Rejected'
                        else:
                            obs_status = 'Selected'
                        if obs_status == 'Selected':
                            ob_data['sel_not_req'] = True
                        else:
                            ob_data['sel_not_req'] = False
                        if obs_status == 'Selected':
                            ob_data['sel_color'] = True
                            ob_data['req_color'] = False
                            ob_data['acc_color'] = False
                            ob_data['rej_color'] = False
                            ob_data['comp_color'] = False
                        elif obs_status == 'Requested':
                            ob_data['sel_color'] = False
                            ob_data['req_color'] = True
                            ob_data['acc_color'] = False
                            ob_data['rej_color'] = False
                            ob_data['comp_color'] = False
                        elif obs_status == 'Accepted':
                            ob_data['sel_color'] = False
                            ob_data['req_color'] = False
                            ob_data['acc_color'] = True
                            ob_data['rej_color'] = False
                            ob_data['comp_color'] = False
                        elif obs_status == 'Completed':
                            ob_data['sel_color'] = False
                            ob_data['req_color'] = False
                            ob_data['acc_color'] = False
                            ob_data['rej_color'] = False
                            ob_data['comp_color'] = True
                        else:
                            ob_data['sel_color'] = False
                            ob_data['req_color'] = False
                            ob_data['acc_color'] = False
                            ob_data['rej_color'] = True
                            ob_data['comp_color'] = False
                        if obs_status == 'Completed':
                            comp_info = File_Details.objects.filter(obs_id=pk, ama_id = u).iterator()
                            ob_data['comp_date'] = next(comp_info).uploaded_at
                        ob_data['obs_name'] = obs.obs_name
                        ob_data['location'] = obs.location
                        ob_data['aper'] = obs.telescope_aper
                        ob_data['flen'] = obs.telescope_flength
                        ob_data['det'] = obs.det_mod
                        ob_data['fov'] = "{:.2f}".format(obs.fov)
                        ob_data['uname'] = u
                        ob_data['obs_img'] = obs.obs_img
                        ob_data['status'] = obs_status
                        ob_data['obs_link'] = 'https://4piastro.com/obs_calc/'+u+'-'+pk
                        ob_data['ama_id'] = obs.user_id
                        lp = obs.SQM
                        if lp == 0.:
                            ob_data['lp'] = 'NA'
                        else:
                            ob_data['lp'] = str("{:.2f}".format(lp))
                        ob_data['pix_scale'] = "{:.2f}".format((200./obs.telescope_flength)*obs.det_pix_scale)
                        obs_data.append(ob_data)
                    context['observatories'] = obs_data
                    return render(request, 'obs_overview_prof.html', context)
            else:
                return HttpResponseNotFound("hello")
        else:
            return redirect('https://4piastro.com/accounts/login')


class remove_obser(View):
    def get(self,request, slug, pk, *args, **kwargs):
        Proposal = next(Obs_Prop.objects.filter(pk = pk).iterator())
        sel_users = Proposal.selected_users.split(',')
        sel_users.remove(slug)
        Proposal.selected_users = ','.join(sel_users)
        if Proposal.unselected_users == '':
            Proposal.unselected_users = slug
        else:
            unsel_users = Proposal.unselected_users.split(',')
            unsel_users.append(slug)
            unsel_users = list(set(unsel_users))
            Proposal.unselected_users = ','.join(unsel_users)
        Proposal.save()
        return redirect('https://4piastro.com/obs/overview/{0}'.format(pk))
