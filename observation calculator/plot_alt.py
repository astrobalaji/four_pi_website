import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
plt.style.use(astropy_mpl_style)

import os
os.chdir('/Users/astrobalaji/Documents/four_pi_live/four_pi_website/observation calculator')

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS, get_sun, get_moon

import pandas as pd
import re
import pytz
import requests
import json

from datetime import datetime

def reformat_str(coords, RA):
    fiiter = re.finditer('\:', coords)
    span_1 = next(fiiter).span()
    span_2 = next(fiiter).span()
    coords_split = list(coords)
    if RA:
        coords_split[span_1[0]] = 'h'
    else:
        coords_split[span_1[0]] = 'd'
    coords_split[span_2[0]] = 'm'
    coords_split.append('s')
    return ''.join(coords_split)

def sky_coords(RA_str, Dec_str):
    return SkyCoord(RA_str, Dec_str, frame = ICRS)

def transform(skcoords, frame):
    return skcoords.transform_to(frame_tonight)

latitude = 13.08
longitude = 80.27

std_stars = pd.read_csv('std_stars.csv', delimiter = ';')

std_stars.rename(columns = {'December':'Dec'}, inplace = True)

std_stars['RA'] = std_stars['RA'].apply(lambda x: reformat_str(x, True))
std_stars['Dec'] = std_stars['Dec'].apply(lambda x: reformat_str(x, False))

std_stars = std_stars[['Star', 'RA', 'Dec']]

std_stars['sky_coords'] = std_stars.apply(lambda x: sky_coords(x['RA'], x['Dec']), axis = 1)

Locat = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg, height=0.1*u.m)

midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

midnight = Time(midnight.strftime('%Y-%m-%d %H:%M:%S'))

delta_midnight = np.linspace(-12, 12, 100)*u.hour


frame_tonight = AltAz(obstime=midnight+delta_midnight,location=Locat)

std_stars['altaz_night'] = std_stars['sky_coords'].apply(lambda x: transform(x, frame_tonight))

sunaltazs_tonight = get_sun(midnight+delta_midnight).transform_to(frame_tonight)
moonaltazs_tonight = get_moon(midnight+delta_midnight).transform_to(frame_tonight)


test = std_stars['altaz_night'][3]
plt.plot(delta_midnight, sunaltazs_tonight.alt, color='r', label='Sun')
plt.plot(delta_midnight, moonaltazs_tonight.alt, color=[0.75]*3, ls='--', label='Moon')
plt.scatter(delta_midnight, test.alt,
            c=test.az, label='M33', lw=0, s=8,
            cmap='viridis')
plt.fill_between(delta_midnight.to('hr').value, 0, 90,
                 sunaltazs_tonight.alt < -0*u.deg, color='0.5', zorder=0)
plt.fill_between(delta_midnight.to('hr').value, 0, 90,
                 sunaltazs_tonight.alt < -18*u.deg, color='k', zorder=0)
plt.colorbar().set_label('Azimuth [deg]')
plt.legend(loc='upper left')
plt.xlim(-12, 12)
plt.xticks(np.arange(13)*2 -12)
plt.ylim(0, 90)
plt.xlabel('Hours from EDT Midnight')
plt.ylabel('Altitude [deg]')
plt.show()


std_stars.head()
