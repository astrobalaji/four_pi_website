from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from datetime import datetime, timedelta
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
from bokeh.models import HoverTool, TapTool, OpenURL, BoxAnnotation, Range1d, BoxAnnotation, DatetimeTickFormatter, Span, Label
from bokeh.embed import components
from bokeh.layouts import row


from .forms import ObsSettings



def magtoflux(mag, tel_aper):
    zero_mag = 3953 #Jy for V band
    delta_lambda = 88e-9 #m
    c = 3e8 #m/s
    tel_aper = tel_aper/10. #cm
    lam = 551e-9 #m
    f_jy = zero_mag*(10**(-mag/2.5)) #Jy
    f_ergs = f_jy*1e-23 # erg/cm^2/s/Hz
    delta_hz = c/delta_lambda # Hz
    f_ergs = f_ergs*delta_hz # erg/cm^2/s/Hz to # erg/cm^2/s
    f_ergs = f_ergs*(np.pi*((tel_aper/2.)**2.)) # ergs/s
    return f_ergs


def calc_fov(pix, pix_scale):
    det_dim = [int(v) for v in pix.split('x')]
    return (det_dim[0]*pix_scale)*(det_dim[1]*pix_scale)

def calculate_SNR(mag, tel_aper, min_snr, pix, pix_scale, SQM, RN, QE):
    exp_start = 0.
    exp_end = 3600.
    exp_times = np.arange(exp_start, exp_end, 0.1)
    fov = calc_fov(pix, pix_scale)
    pixels = [int(p) for p in pix.split('x')]
    npix = pixels[0]*pixels[1]
    snr = np.empty(exp_times.shape[0])
    h = 6.62e-27
    c = 2.99e10
    lam = 551e-7
    for i in range(exp_times.shape[0]):
         N = (magtoflux(mag, tel_aper)*exp_times[i])/(h*c/lam)
         if SQM != 0.:
             B = (magtoflux(SQM*fov, tel_aper)*exp_times[i])/(h*c/lam)
             snr[i] = (N*(QE/100.))/np.sqrt((N*(QE/100.))+(B*(QE/100.))+(npix*(RN**2.)))
         else:
             snr[i] = (N*(QE/100.))/np.sqrt((N*(QE/100.))+(npix*(RN**2.)))
    if (3*min_snr)<=snr[1]:
        snr_filt = snr[:20]
        exp_times_filt = exp_times[:20]
    else:
        if np.max(snr) >= 3*min_snr:
            snr_filt = snr[np.where(np.logical_and((snr>=min_snr-2), (snr<=3*min_snr)))]
            exp_times_filt = exp_times[np.where(np.logical_and((snr>=min_snr), (snr<=3*min_snr)))[0]]
        else:
            snr_filt = snr[np.where(snr>=min_snr-2)]
            exp_times_filt = exp_times[np.where(snr>=min_snr-2)]

    return list(exp_times_filt), list(snr_filt)

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

            return render(request, 'obs_home_ama.html', context)
        else:
            data = Obs_Prop.objects.filter(pk=pk).iterator()
            Proposal = next(data)

            req_obs = Proposal.requested_users.split(',')
            acc_obs = Proposal.accepted_users.split(',')
            if (slug in req_obs) or (slug in acc_obs):
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
            midnight_end = Proposal.start_date+timedelta(days = Proposal.no_of_nights)
            utcoffset = time_zone*u.hour

            midnight_xaxis = Time(midnight.strftime('%Y-%m-%d %H:%M:%S'))

            midnight = Time(midnight.strftime('%Y-%m-%d %H:%M:%S'))-utcoffset
            midnight_end = Time(midnight_end.strftime('%Y-%m-%d %H:%M:%S'))-utcoffset



            delta_midnight = np.linspace(-12, 12, 1000)*u.hour

            frame_tonight = AltAz(obstime=midnight+delta_midnight,location=Locat)
            frame_end = AltAz(obstime=midnight_end+delta_midnight,location=Locat)


            altaz = self.transform(skycoord, frame_tonight)
            altaz_end = self.transform(skycoord, frame_end)


            sunaltazs_tonight = get_sun(midnight+delta_midnight).transform_to(frame_tonight)
            moonaltazs_tonight = get_moon(midnight+delta_midnight).transform_to(frame_tonight)



            time_arr = midnight_xaxis+delta_midnight
            time_arr = time_arr.value


            time_str_arr = [datetime.strptime(t,'%Y-%m-%d %H:%M:%S.%f') for t in time_arr]

            SQM = Observer.SQM

            exps, snr = calculate_SNR(Proposal.magnitude, Observer.telescope_aper, Proposal.min_snr, Observer.detector_dimensions, Observer.det_pix_scale, SQM, Observer.read_noise, Observer.QE)

            p1 = figure(x_axis_label='Local time',y_axis_label='Altitude (degs)')
            #p1.line(time_str_arr, sunaltazs_tonight.alt, line_color = 'red', legend_label = 'Sun')
            p1.line(time_str_arr, moonaltazs_tonight.alt, line_color = 'green', legend_label = 'Moon')
            p1.line(time_str_arr, altaz.alt, line_color = 'blue', legend_label = 'Obj. (starting date)')
            p1.line(time_str_arr, altaz_end.alt, line_color = 'blue', line_dash = 'dashed', legend_label = 'Obj. (ending date)')
            p1.toolbar.logo = None
            p1.toolbar_location = None
            p1.y_range = Range1d(0,90)

            p1.legend.label_text_font_size = '10pt'

            twilight_lims_arr = sunaltazs_tonight.alt < -0*u.deg
            night_lims_arr = sunaltazs_tonight.alt < -18*u.deg

            twilight_lim_lower = np.nonzero(twilight_lims_arr)[0].min()
            twilight_lim_upper = np.nonzero(twilight_lims_arr)[0].max()

            night_lim_lower = np.nonzero(night_lims_arr)[0].min()
            night_lim_upper = np.nonzero(night_lims_arr)[0].max()



            twilight_box = BoxAnnotation(left = time_str_arr[twilight_lim_lower], right = time_str_arr[twilight_lim_upper], fill_alpha = 0.4, fill_color = 'grey')
            night_box = BoxAnnotation(left = time_str_arr[night_lim_lower], right = time_str_arr[night_lim_upper], fill_alpha = 0.4, fill_color = 'black')

            p1.add_layout(twilight_box)
            p1.add_layout(night_box)
            hline = Span(location=30, dimension='width', line_color='brown', line_width=3, line_dash = 'dashed')
            my_label = Label(x=time_str_arr[0], y=30, text='30° alt.')

            #my_label_2 = Label(x=time_str_arr[int(len(time_str_arr)/2)-112], y=87, text='Night time at start')


            p1.add_layout(hline)
            p1.add_layout(my_label)
            #p1.add_layout(my_label_2)


            obj_alts = np.array([round(t) for t in altaz.alt.deg])

            locs = np.where(obj_alts == 30.)[0]
            try:
                vline_1 = Span(location = time_str_arr[locs[0]], dimension = 'height', line_color = 'black', line_width = 3, line_dash = 'dashed')
                vline_2 = Span(location = time_str_arr[locs[-1]], dimension = 'height', line_color = 'black', line_width = 3, line_dash = 'dashed')

                p1.add_layout(vline_1)
                p1.add_layout(vline_2)
            except:
                print('not below 30degs')


            p1.xaxis.formatter=DatetimeTickFormatter(
                                                    hours=["%H:%M"],
                                                    days=["%H:%M"],
                                                    months=["%H:%M"],
                                                    years=["%H:%M"],
                                                    )


            p2 = figure(x_axis_label = 'Exposure time (s)', y_axis_label='SNR')
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
            send_req_email(slug, Proposal.obs_title, Proposal.description, Proposal.pk)
            self.req_obs(request, slug, pk)
            return redirect('/obs/overview/'+pk)
        else:
            return redirect('/obs_calc/'+slug+'-'+pk)

def send_req_email(ama_uname, obs_title, obs_desc, obs_pk):
    obs_obj = next(User.objects.filter(username=ama_uname).iterator())
    subject = 'Activate Your 4pi Account'
    fname = obs_obj.first_name
    lname = obs_obj.last_name
    full_name = fname+' '+lname
    subject = 'You have received an observtion request'
    message = render_to_string('emails/request_email.html', {
        'user_fname': full_name,
        'obs_title': obs_title,
        'obs_desc': obs_desc,
        'obs_pk': obs_pk
    })
    send_mail(subject = subject, message = message, from_email = 'hello@4pi-astro.com', recipient_list = [obs_obj.email])
