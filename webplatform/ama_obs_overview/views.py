from django.shortcuts import render
from django.views.generic import View
from obs_propose.models import Obs_Prop

# Create your views here.
class ama_overview_views(View):
    def get(self, request, pk, *args, **kwargs):

        res = Obs_Prop.objects.filter(pk=pk).iterator()
        Proposal = next(res)
        prop_data = {}
        prop_data['title'] = Proposal.obs_title
        prop_data['description'] = Proposal.description
        prop_data['obs_type'] = Proposal.obs_type
        prop_data['field_type'] = Proposal.field_type
        prop_data['fov'] = Proposal.fov
        prop_data['mag'] = Proposal.magnitude
        prop_data['ra'] = Proposal.coords_ra
        prop_data['dec'] = Proposal.coords_dec
        prop_data['settings'] = Proposal.settings
        prop_data['req_users'] = Proposal.requested_users
        prop_data['accepted_users'] = Proposal.accepted_users

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

        return render(request, 'obs_overview_ama.html', prop_data)

class accept_obs(View):
    def get(self, request, slug, pk, *args, **kwargs):
        res = Obs_Prop.objects.filter(pk=pk).iterator()
        Proposal = next(res)
        if Proposal.requested_users != slug:
            Proposal.requested_users = Proposal.requested_users.replace(slug+',', '')
        else:
            Proposal.requested_users = ''
        if Proposal.requested_users == '':
            Proposal.requested_users = slug
        else:
            acc_users = Proposal.accepted_users.split(',')
            acc_users.append(slug)
            Proposal.accepted_users = ','.join(acc_users)
            Proposal.save()
        return render(request, 'autoclose.html')

class reject_obs(View):
    def get(self, request, slug, pk, *args, **kwargs):
        res = Obs_Prop.objects.filter(pk=pk).iterator()
        Proposal = next(res)
        if Proposal.requested_users != slug:
            Proposal.requested_users = Proposal.requested_users.replace(slug+',', '')
        else:
            Proposal.requested_users = ''
        if Proposal.requested_users == '':
            Proposal.requested_users = slug
        else:
            rej_users = Proposal.rejected_users.split(',')
            rej_users.append(slug)
            Proposal.rejected_users = ','.join(rej_users)
            Proposal.save()
        return render(request, 'autoclose.html')
