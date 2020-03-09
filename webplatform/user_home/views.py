from django.shortcuts import render, redirect
from amateurOnboarding.models import AmaOB
from proOnboarding.models import proOB
from obs_propose.models import Obs_Prop
import arxiv
import ast

def get_arxiv(field):
    results = arxiv.query(query=field, sort_by='submittedDate', sort_order = 'descending', max_results = 10)
    res_out = []
    for res in results:
        r_temp = {}
        r_temp['author'] = res['author']
        r_temp['title'] = res['title']
        r_temp['summary'] = res['summary']
        r_temp['pdf'] = res['pdf_url']
        res_out.append(r_temp)
    return res_out

def get_obs(uname):
    obsers = []
    it = Obs_Prop.objects.filter(user_id = uname).iterator()
    for i in it:
        obs = {}
        obs['title'] = i.obs_title
        obs['submitted_on'] = i.submitted_on
        obs['status'] = i.status
        obs['pk'] = i.pk
        obsers.append(obs)
    return obsers

def get_ama_new_obs(uname):
    obsers = []
    res = Obs_Prop.objects.filter(requested_users__contains=uname).iterator()
    for i in res:
        obs = {}
        obs['title'] = i.obs_title
        obs['summary'] = i.description
        obs['pid'] = i.pk
        obsers.append(obs)
    return obsers

def get_ama_sel_obs(uname):
    obsers = []
    res = Obs_Prop.objects.filter(accepted_users__contains=uname).iterator()
    for i in res:
        obs = {}
        obs['title'] = i.obs_title
        obs['description'] = i.description
        obs['pk'] = i.pk
        obsers.append(obs)
    return obsers

def get_ama_comp_obs(uname):
    obsers = []
    res = Obs_Prop.objects.filter(completed_users__contains=uname).iterator()
    for i in res:
        obs = {}
        obs['title'] = i.obs_title
        obs['description'] = i.description
        obs['credits'] = 0
        obsers.append(obs)
    return obsers


def checkDB(uname):
    try:
        amaOB_check = AmaOB.objects.filter(user_id = uname).count()
    except:
        amaOB_check = 0

    proOB_check = proOB.objects.filter(user_id = uname)
    proOB_check = proOB_check.count()
    if amaOB_check!=0:
        return 'ama'
    elif proOB_check!=0:
        return 'pro'
    else:
        return 'NA'
def index(request):
    if request.user.is_authenticated:
        fname = request.user.first_name
        lname = request.user.last_name
        full_name = fname+' '+lname
        uname = request.user.username
        dir = checkDB(uname)
        if dir == 'pro':
            it = proOB.objects.filter(user_id = uname).iterator()
            field = next(it).field_of_interest
            arxiv_res = get_arxiv(field)
            obs_res = get_obs(uname)
            if len(obs_res) == 0:
                tab_disp = False
            else:
                tab_disp = True
            context = {'fname':full_name,'arxiv_res':arxiv_res, 'tab_disp':tab_disp, 'obs_res':obs_res}
            return render(request, 'user_home_prof.html', context)
        elif dir == 'ama':
            res = AmaOB.objects.filter(user_id = uname).iterator()
            AmaData = next(res)
            #Ama_Credits = ast.literal_eval(AmaData.credits)
            #Ama_total_credits = AmaData.total_credits
            newobs = get_ama_new_obs(uname)
            selobs = get_ama_sel_obs(uname)
            compobs = get_ama_comp_obs(uname)
            if len(newobs) == 0:
                newobsdisp = False
            else:
                newobsdisp = True
            if len(selobs) == 0:
                selobsdisp = False
            else:
                selobsdisp = True
            if len(compobs) == 0:
                compobsdisp = False
            else:
                compobsdisp = True
            obs_home_link = 'https://4pi-astro.com/obs_calc/'+uname+'-0'
            context = {'fname':full_name, 'newobsdisp':newobsdisp, 'selobsdisp':selobsdisp, 'compobsdisp':compobsdisp, 'newobs':newobs, 'selobs':selobs, 'compobs':compobs, 'obs_home_link':obs_home_link, 'total_credits':0}
            return render(request, 'user_home_ama.html', context)
        else:
            return redirect('activate/dir_sel/')#render(request, 'temphome.html', {'full_name':full_name})
    else:
        return redirect('/accounts/login')
