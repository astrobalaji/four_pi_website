from django.shortcuts import render, redirect
from .forms import AmaOnboarding
from django.views.generic import View
import numpy as np
from .models import AmaOB
import requests as req
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
from math import sin, cos, sqrt, atan2

# Create your views here.

def calc_fov(flen, pixscale, dims):
    dims = [int(x) for x in dims.split('x')]
    arc_per_pix = 200.*pixscale/flen
    return np.sqrt((dims[0]**2.)+(dims[1]**2.))*arc_per_pix/60.

'''def get_lp_data():
    html_content = req.get('http://www.unihedron.com/projects/darksky/database/index.php?csv=true').content
    soup = BeautifulSoup(html_content, parser = 'html')
    csv_text = soup.find('pre').text
    csv_io = StringIO(csv_text)
    df = pd.read_csv(csv_io)
    df.columns = df.columns.str.replace(' ', '')
    df.Latitude = df.Latitude.str.replace(' ', '')
    df.Longitude = df.Longitude.str.replace(' ', '')
    df = df[['Latitude', 'Longitude', 'Brightness']]
    df = df[df['Latitude'] != '']
    df = df[df['Longitude'] != '']
    df.Latitude = df.Latitude.astype(float)
    df.Longitude = df.Longitude.astype(float)
    return df

def dist(row,lat, lon):
    R = 6373.0
    dlon = row['Longitude'] - lon
    dlat = row['Latitude'] - lat
    a = (sin(dlat/2))**2 + cos(row['Latitude']) * cos(lat) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def get_SQM_reading(lat, lon):
    lp_df = get_lp_data()
    lp_df['distance'] = lp_df.apply(lambda x: dist(x, lat, lon), axis = 1)
    lp_df_sel = lp_df[lp_df['distance']<=100.]
    if len(lp_df_sel) != 0:
        return lp_df_sel['Brightness'].mean()
    else:
        return 0.
'''

lp_df = pd.read_csv('datafiles/LP_data.csv')

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

class AmaOBViews(View):
    form_class = AmaOnboarding

    def get(self, request):
        form = self.form_class()

        if request.user.is_authenticated:
            fname = request.user.first_name
            lname = request.user.last_name
            full_name = fname+' '+lname
            context = {'form':form, 'full_name':full_name}
            return render(request, 'Onboarding/AmaOb.html', context)
        else:
            return redirect('https://4piastro.com/accounts/login')

    def post(self, request):
        form = self.form_class(request.POST ,request.FILES)
        if form.is_valid():
            observatory = form.save(commit=False)
            uname = request.user.username
            observatory.user_id = uname
            fov = calc_fov(observatory.telescope_flength, observatory.det_pix_scale, observatory.detector_dimensions)
            observatory.fov = fov
            if observatory.read_noise == None:
                observatory.read_noise = 0.
            if observatory.QE == None:
                observatory.QE = 100.
            observatory.SQM = get_SQM_reading(observatory.lat, observatory.lon)
            observatory.save()
            return redirect('/user/home/')
        else:
            return redirect('/onboarding/amateur')
