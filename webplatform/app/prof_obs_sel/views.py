from django.shortcuts import render, redirect


import bokeh

from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.callbacks import CustomJS
from bokeh.models import HoverTool, TapTool, OpenURL, WheelZoomTool, PanTool
from bokeh.embed import components
from bokeh.layouts import row

from datetime import datetime, timedelta
import numpy as np
import math
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS, get_sun, get_moon

from ast import literal_eval

from amateurOnboarding.models import AmaOB
from obs_propose.models import Obs_Prop

from bokeh.tile_providers import get_provider, Vendors

from django.views.generic import View
from django.http import HttpResponseNotFound

from .forms import ObsDatePick



sel_users = []



def sky_coords(RA_str, Dec_str):
    return SkyCoord(RA_str, Dec_str, frame = ICRS)

def transform(skcoords, frame_tonight):
    return skcoords.transform_to(frame_tonight)


def check_threshold(arr, threshold):
    check = False
    if threshold<=max(arr):
        check = True
    return check

def check_dates(booked_dates, start_date, no_of_nights):
    check = False
    if booked_dates == '':
        return False
    dates = booked_dates.split(',')#[datetime.strptime(d, '%Y-%m-%d') for d in booked_dates.split(',')]
    req_nights = []
    for i in range(no_of_nights+1):
        req_nights.append(start_date+timedelta(days=i))
    req_nights = [r_n.strftime('%Y-%m-%d') for r_n in req_nights]
    intersect = list(set(dates).intersection(req_nights))
    if len(intersect) != 0.:
        check = True
    return check

def check_observability(prop_pk, user_id):
    data = Obs_Prop.objects.filter(pk=prop_pk).iterator()
    Proposal = next(data)
    data = AmaOB.objects.filter(user_id=user_id).iterator()
    Observer = next(data)
    latitude = Observer.lat
    longitude = Observer.lon

    time_zone = Observer.tz

    RA = Proposal.coords_ra
    dec = Proposal.coords_dec

    skycoord = sky_coords(RA, dec)

    Locat = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg, height=0.1*u.m)

    midnight = Proposal.start_date
    utcoffset = time_zone*u.hour

    midnight = Time(midnight.strftime('%Y-%m-%d %H:%M:%S'))-utcoffset

    delta_midnight = np.linspace(-6, 6, 1000)*u.hour

    frame_tonight = AltAz(obstime=midnight+delta_midnight,location=Locat)

    altaz = transform(skycoord, frame_tonight).altaz

    sunaltazs_tonight = get_sun(midnight+delta_midnight).transform_to(frame_tonight).altaz
    moonaltazs_tonight = get_moon(midnight+delta_midnight).transform_to(frame_tonight).altaz

    azs = [a.deg for a in altaz.az]
    sunazs = [a.deg for a in sunaltazs_tonight.az]
    moonazs = [a.deg for a in moonaltazs_tonight.az]

    deltsunaz = [abs(a) for a in list(np.array(azs)-np.array(sunazs))]
    deltmoonaz = [abs(a) for a in list(np.array(azs)-np.array(moonazs))]


    alts = [a.deg for a in altaz.alt]

    checksunaz = check_threshold(deltsunaz, 60)
    checkmoonaz = check_threshold(deltmoonaz, 60)
    checkalt = check_threshold(alts, 30)

    check_night_time = sunaltazs_tonight.alt.min() < -18.*u.deg


    ### checking time for obj alts
    time_str_arr = midnight+delta_midnight
    time_arr = np.array([datetime.strptime(t,'%Y-%m-%d %H:%M:%S.%f') for t in time_str_arr.value])

    time_arr_lims = time_arr[np.where(np.array(alts)>=30.)]
    if len(time_arr_lims) > 1.:
        time_diff = time_arr_lims[-1]-time_arr_lims[0]

        time_diff_check = (time_diff.total_seconds()/3600.) >= 4.0
    else:
        time_diff_check = False

    if checksunaz and checkmoonaz and checkalt and check_night_time and time_diff_check:
        return True
    else:
        return False




def coords2merc(lat, lon):
    RADIUS = 6378137.0
    merc_lat = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * RADIUS
    merc_lon = math.radians(lon) * RADIUS
    return merc_lat, merc_lon

def callback_func(attr, old, new):
    selections = new['1d']['indices']
    unames = []
    for index in selections:
        unames.append(source.data['name'][index])
        #print("TapTool callback executed on Patch {}".format(patch_name))
    return unames


def plot_world_map(ds):
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)
    selected_src = ColumnDataSource(dict(indices=[]))
    source = ColumnDataSource(ds)
    hovert = HoverTool(tooltips = [('city', '@name'), ('timezone','@tz'), ('aperture', '@aper'), ('focal length', '@focal_length'), ('detector', '@det_name'), ('fov', '@fov')])

    p = figure(x_range=(-120000, 190000), y_range=(-12000000, 12000000),
           x_axis_type="mercator", y_axis_type="mercator", plot_width = 1135, plot_height = 600, tools = 'tap')
    p.add_tile(tile_provider)

    p.circle(x='x',y='y', alpha = 0.5, size = 10,color = "red", source=source)


    p.add_tools(hovert)
    #p.add_tools(WheelZoomTool())
    #p.add_tools(PanTool())
    taptool = p.select(type=TapTool)
    p.toolbar.logo = None
    p.toolbar_location = None
    url = "https://4piastro.com/obssel/@uid-@pid"
    taptool.callback = OpenURL(url=url)

    script, div = components(p)

    return {'script':script, 'div':div}
class obs_sel_views(View):
    form_class = ObsDatePick
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            obj = Obs_Prop.objects.filter(pk=pk)#filter(user_id=request.user.username).order_by('id')
            proposal = next(obj.iterator())
            if request.user.username == proposal.user_id:
                ra = proposal.coords_ra
                dec = proposal.coords_dec
                it = AmaOB.objects.filter(fov__gte=proposal.min_fov, fov__lte=proposal.max_fov).iterator()
                lat = []
                lon = []
                lat_n = []
                lon_n = []
                name = []
                tz = []
                aper = []
                focal_length = []
                det_name = []
                fov = []
                user_id = []
                pklist = []
                users_booked = []
                observability_checks = []
                users_booked_check = False
                obs_not_checks = False
                for data in it:
                    if check_dates(data.booked_dates, proposal.start_date, proposal.no_of_nights):
                        users_booked.append(True)
                        continue
                    else:
                        users_booked.append(False)
                    if not check_observability(proposal.pk, data.user_id):
                        observability_checks.append(True)
                        continue
                    else:
                        observability_checks.append(False)
                    if (data.user_id in proposal.selected_users.split(',')) or (data.user_id in proposal.unselected_users.split(',')):
                        continue
                    temp_lat, temp_lon = coords2merc(data.lat, data.lon)
                    lat.append(temp_lat)
                    lon.append(temp_lon)
                    lat_n.append(data.lat)
                    lon_n.append(data.lon)
                    name.append(data.location)
                    tz.append(data.tz)
                    aper.append(data.telescope_aper)
                    focal_length.append(data.telescope_flength)
                    det_name.append(data.det_mod)
                    fov.append(data.fov)
                    user_id.append(data.user_id)
                    pklist.append(proposal.pk)
                if all(users_booked) and (len(users_booked)!=0):
                    users_booked_check = True
                elif all(observability_checks) and (len(observability_checks) !=0):
                    obs_not_checks = True
                if users_booked_check or obs_not_checks:
                    init_data = {'start_date':proposal.start_date, 'no_of_nights':proposal.no_of_nights}
                    form = self.form_class(initial = init_data)
                else:
                    form = ''

                tz = ['UTC+{0}'.format(t) if t>0 else 'UTC{0}'.format(t) for t in tz]
                ds = dict(x=lon, y=lat,lat=lat_n, lon=lon_n, name=name, tz=tz, aper=aper, focal_length=focal_length, det_name=det_name, fov=fov, uid=user_id, pid=pklist)
                plt = plot_world_map(ds)
                plt['pk'] = proposal.pk
                plt['users_booked_check'] = users_booked_check
                plt['obs_not_checks'] = obs_not_checks
                plt['form'] = form
                return render(request, 'obs_sel.html', plt)
            else:
                return HttpResponseNotFound("hello")
        else:
            return redirect('https://4piastro.com/accounts/login')
    def post(self, request,  pk, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            obs_dates = form.cleaned_data
            data = next(Obs_Prop.objects.filter(pk = pk).iterator())
            data.start_date = obs_dates.get('start_date')
            data.no_of_nights = obs_dates.get('no_of_nights')
            data.save()
            return redirect('/obs_sel/{0}'.format(pk))

class SelectObservatory(View):
    def get(self, request, slug, pk, *args, **kwargs):
        obj = Obs_Prop.objects.filter(pk=pk)
        proposal = next(obj.iterator())
        if proposal.selected_users != '':
            sel_users = proposal.selected_users.split(',')
            sel_users.append(slug)
            proposal.selected_users = ','.join(list(set(sel_users)))
            unsel_users = proposal.unselected_users.split(',')
            unsel_users = [u for u in unsel_users if u != slug]
            proposal.unselected_users = ','.join(unsel_users)
        else:
            proposal.selected_users = slug
            unsel_users = proposal.unselected_users.split(',')
            unsel_users = [u for u in unsel_users if u != slug]
            proposal.unselected_users = ','.join(unsel_users)
        proposal.save()
        return render(request, 'autoclose.html')
