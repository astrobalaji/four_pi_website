from django.shortcuts import render, render_to_response
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.callbacks import CustomJS
from bokeh.models import HoverTool, TapTool, OpenURL
from bokeh.embed import components
from datetime import datetime
import numpy as np
import math
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS, get_sun, get_moon

from amateurOnboarding.models import AmaOB
from obs_propose.models import Obs_Prop

from bokeh.tile_providers import get_provider, Vendors

from django.views.generic import View

sel_users = []

tile_provider = get_provider(Vendors.CARTODBPOSITRON)


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


def plot_world_map(source):
    selected_src = ColumnDataSource(dict(indices=[]))
    hovert = HoverTool(tooltips = [('lat', '@lat'), ('lon', '@lon'), ('city', '@name'), ('aperture', '@aper'), ('focal length', '@focal_length'), ('detector', '@det_name'), ('fov', '@fov')])

    p = figure(x_range=(-180000, 180000), y_range=(-20000000, 20000000),
           x_axis_type="mercator", y_axis_type="mercator", plot_width = 1135, plot_height = 600, tools = 'tap')
    p.add_tile(tile_provider)

    p.circle(x='x',y='y', alpha = 0.5, size = 7, source=source)


    p.add_tools(hovert)
    taptool = p.select(type=TapTool)
    p.toolbar.logo = None
    p.toolbar_location = None
    url = "http://localhost:8000/obs_sel/@uid-@pid"
    taptool.callback = OpenURL(url=url)

    script, div = components(p)

    return {'script':script, 'div':div}

def index(request):
    obj = Obs_Prop.objects.filter(user_id=request.user.username).order_by('id')
    proposal = next(obj.iterator())
    ra = proposal.coords_ra
    dec = proposal.coords_dec
    it = AmaOB.objects.filter(fov__gte=proposal.fov).iterator()
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
    for data in it:
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
        fov.append(data.fov/60)
        user_id.append(data.user_id)
        pklist.append(proposal.pk)
    ds = ColumnDataSource(data = dict(x=lon, y=lat,lat=lat_n, lon=lon_n, name=name, tz=tz, aper=aper, focal_length=focal_length, det_name=det_name, fov=fov, uid=user_id, pid=pklist))
    plt = plot_world_map(ds)
    plt['pk'] = proposal.pk
    return render(request, 'obs_sel.html', plt)

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
