from django.shortcuts import render, redirect
from django.views.generic import View
from datetime import datetime
import numpy as np
import math
import requests as req


import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS, get_sun, get_moon

from amateurOnboarding.models import AmaOB
from obs_propose.models import Obs_Prop

from ast import literal_eval

from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.callbacks import CustomJS
from bokeh.models import HoverTool, TapTool, OpenURL, BoxAnnotation, Range1d
from bokeh.embed import components
from bokeh.layouts import row


from prof_obs_overview.views import get_SQM_reading

from .forms import ObsSettings



def magtoflux(mag, tel_aper):
    zero_mag = 3953 #Jy for V band
    delta_lambda = 88e-9
    c = 3e8
    tel_aper = tel_aper/10.
    lam = 551e-9
    f_jy = zero_mag*(10**(-mag/2.5))
    f_ergs = f_jy*1e-23 # erg/cm^2/s/Hz
    delta_hz = c/delta_lambda
    f_ergs = f_ergs*delta_hz # erg/cm^2/s/Hz to # erg/cm^2/s
    f_ergs = f_ergs*(np.pi*((tel_aper/2.)**2.)) # ergs/s
    return f_ergs
def calc_fov(pix, pix_scale):
    det_dim = [int(v) for v in pix.split('x')]
    return (det_dim[0]*pix_scale)*(det_dim[1]*pix_scale)

def calculate_SNR(mag, tel_aper, exp_start, exp_end, pix, pix_scale, SQM, RN):
    exp_times = list(np.arange(exp_start, exp_end, 0.1))
    fov = calc_fov(pix, pix_scale)
    pixels = [int(p) for p in pix.split('x')]
    npix = pixels[0]*pixels[1]
    snr = []
    for e in exp_times:
         N = magtoflux(mag, tel_aper)*e
         B = magtoflux(SQM*fov, tel_aper)*e
         SNR = N/np.sqrt(N+B+(npix*(RN**2.)))
         snr.append(SNR)
    return exp_times, snr

def get_weather(lat,lon):
    url = "http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&units=metric&appid=8b502954a629d709d6ec5d52e5e54722".format(lat,lon)
    data = req.get(url)
    res = data.json()
    temp_min = res['main']['temp_min']
    temp_max = res['main']['temp_max']
    hum = res['main']['humidity']
    clouds = res['clouds']['all']

    return str(temp_min)+'°c', str(temp_max)+'°c', str(hum)+'%', str(clouds)+'%'

# Create your views here.
class obs_calc_views(View):
    form_class = ObsSettings
    def sky_coords(self,RA_str, Dec_str):
        return SkyCoord(RA_str, Dec_str, frame = ICRS)

    def transform(self,skcoords, frame_tonight):
        return skcoords.transform_to(frame_tonight)

    def req_obs(self, request, slug, pk):
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


    def get(self, request, slug, pk, *args, **kwargs):
        if pk == '0':
            data = AmaOB.objects.filter(user_id=slug).iterator()
            Observer = next(data)
            min_temp, max_temp, hum, clouds = get_weather(Observer.lat, Observer.lon)
            context = {'obs_title':Observer.obs_name,
                        'obs_img':Observer.obs_img,
                        'loc':Observer.location,
                        'tel_aper':Observer.telescope_aper,
                        'tel_flen':Observer.telescope_flength,
                        'det_name':Observer.det_mod,
                        'fov':Observer.fov,
                        'min_temp':min_temp,
                        'max_temp':max_temp,
                        'hum':hum,
                        'clouds':clouds,
                        }

            return render(request, 'obs_home.html', context)
        else:
            data = Obs_Prop.objects.filter(pk=pk).iterator()
            Proposal = next(data)

            req_obs = Proposal.requested_users.split(',')
            if slug in req_obs:
                requested = True
                req_exp = literal_eval(Proposal.exps)[slug]
                req_sets = literal_eval(Proposal.settings)[slug]
            else:
                requested = False
                req_exp = 0
                req_sets = ''

            data = AmaOB.objects.filter(user_id=slug).iterator()
            Observer = next(data)
            latitude = Observer.lat
            longitude = Observer.lon

            time_zone = Observer.tz

            RA = Proposal.coords_ra
            dec = Proposal.coords_dec

            skycoord = self.sky_coords(RA, dec)

            Locat = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg, height=0.1*u.m)

            midnight = Proposal.start_date
            utcoffset = time_zone*u.hour

            midnight = Time(midnight.strftime('%Y-%m-%d %H:%M:%S'))-utcoffset

            delta_midnight = np.linspace(-12, 12, 1000)*u.hour

            frame_tonight = AltAz(obstime=midnight+delta_midnight,location=Locat)

            altaz = self.transform(skycoord, frame_tonight)

            sunaltazs_tonight = get_sun(midnight+delta_midnight).transform_to(frame_tonight)
            moonaltazs_tonight = get_moon(midnight+delta_midnight).transform_to(frame_tonight)

            SQM = get_SQM_reading(latitude, longitude)

            exps, snr = calculate_SNR(Proposal.magnitude, Observer.telescope_aper, Proposal.exp_min, Proposal.exp_max, Observer.detector_dimensions, Observer.det_pix_scale, SQM, Observer.read_noise)

            p1 = figure(x_axis_label='Hours to midnight',y_axis_label='Altitude')
            p1.line(delta_midnight, sunaltazs_tonight.alt, line_color = 'red', legend_label = 'Sun')
            p1.line(delta_midnight, moonaltazs_tonight.alt, line_color = 'green', legend_label = 'Moon')
            p1.line(delta_midnight, altaz.alt, line_color = 'blue', legend_label = 'Object')
            p1.toolbar.logo = None
            p1.toolbar_location = None
            p1.y_range = Range1d(0,90)

            p2 = figure(x_axis_label = 'exposure time (s)', y_axis_label='SNR')
            p2.line(exps, snr)
            p2.toolbar.logo = None
            p2.toolbar_location = None

            plot = row(p1, p2)

            script, div = components(plot)
            coords = RA+' '+dec


            form = self.form_class()

            min_temp, max_temp, hum, clouds = get_weather(Observer.lat, Observer.lon)
            context = {'script':script,
                        'div':div,
                        'obs_title':Observer.obs_name,
                        'obs_img':Observer.obs_img,
                        'coords':coords,
                        'date':midnight,
                        'loc':Observer.location,
                        'tel_aper':Observer.telescope_aper,
                        'tel_flen':Observer.telescope_flength,
                        'det_name':Observer.det_mod,
                        'fov':Observer.fov,
                        'min_temp':min_temp,
                        'max_temp':max_temp,
                        'hum':hum,
                        'clouds':clouds,
                        'form':form,
                        'requested':requested,
                        'req_exp': req_exp,
                        'req_sets': req_sets}

            return render(request, 'obs_home.html', context)
    def post(self, request, slug, pk, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            obs_settings = form.cleaned_data

            data = Obs_Prop.objects.filter(pk=pk).iterator()
            Proposal = next(data)

            if Proposal.settings == '':
                Proposal.settings = {slug:obs_settings.get('further_instructions')}
            else:
                settings = literal_eval(Proposal.settings)
                settings[slug] = obs_settings.get('further_instructions')
                Proposal.settings = str(settings)
            if Proposal.exps == '':
                Proposal.exps = str({slug:obs_settings.get('exposure_time')})
            else:
                exps = literal_eval(Proposal.exps)
                exps[slug] = obs_settings.get('exposure_time')
                Proposal.exps = str(exps)
            Proposal.save()
            self.req_obs(request, slug, pk)
            return redirect('/obs/overview/'+pk)
        else:
            return redirect('/obs_calc/'+slug+'-'+pk)
