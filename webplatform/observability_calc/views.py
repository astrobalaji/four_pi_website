from django.shortcuts import render
from django.views.generic import View
from datetime import datetime
import numpy as np
import math
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS, get_sun, get_moon

from amateurOnboarding.models import AmaOB
from obs_propose.models import Obs_Prop


from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.callbacks import CustomJS
from bokeh.models import HoverTool, TapTool, OpenURL, BoxAnnotation, Range1d
from bokeh.embed import components


# Create your views here.
class obs_calc_views(View):
    def sky_coords(self,RA_str, Dec_str):
        return SkyCoord(RA_str, Dec_str, frame = ICRS)

    def transform(self,skcoords, frame_tonight):
        return skcoords.transform_to(frame_tonight)

    def get(self, request, slug, pk, *args, **kwargs):
        data = Obs_Prop.objects.filter(pk=pk).iterator()
        Proposal = next(data)
        data = AmaOB.objects.filter(user_id=slug).iterator()
        Observer = next(data)
        latitude = Observer.lat
        longitude = Observer.lon

        time_zone = Observer.tz

        RA = Proposal.coords_ra
        dec = Proposal.coords_dec

        skycoord = self.sky_coords(RA, dec)

        Locat = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg, height=0.1*u.m)

        midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        utcoffset = time_zone*u.hour

        midnight = Time(midnight.strftime('%Y-%m-%d %H:%M:%S'))-utcoffset

        delta_midnight = np.linspace(-12, 12, 1000)*u.hour

        frame_tonight = AltAz(obstime=midnight+delta_midnight,location=Locat)

        altaz = self.transform(skycoord, frame_tonight)

        sunaltazs_tonight = get_sun(midnight+delta_midnight).transform_to(frame_tonight)
        moonaltazs_tonight = get_moon(midnight+delta_midnight).transform_to(frame_tonight)



        plot = figure(x_axis_label='Hours to midnight',y_axis_label='Altitude')
        plot.line(delta_midnight, sunaltazs_tonight.alt, line_color = 'red', legend_label = 'Sun')
        plot.line(delta_midnight, moonaltazs_tonight.alt, line_color = 'green', legend_label = 'Moon')
        plot.line(delta_midnight, altaz.alt, line_color = 'blue', legend_label = 'Object')
        plot.toolbar.logo = None
        plot.toolbar_location = None
        plot.y_range = Range1d(0,90)
        script, div = components(plot)
        coords = RA+' '+dec
        return render(request, 'obs_calc.html', {'script':script, 'div':div, 'obs_title':Observer.obs_name, 'coords':coords, 'date':midnight, 'loc':Observer.location})
