from django.db import models

# Create your models here.
class AmaOB(models.Model):
    obs_name = models.CharField(max_length = 200)
    location = models.CharField(max_length=200)
    lat = models.FloatField()
    lon = models.FloatField()
    tz = models.FloatField()
    avail = models.BooleanField()
    telescope_aper = models.FloatField()
    telescope_flength = models.FloatField()
    det_mod = models.CharField(max_length=200)
    det_pix_scale = models.FloatField()
    detector_dimensions = models.CharField(max_length=200)
    read_noise = models.FloatField()
    user_id = models.CharField(max_length=200)
    fov = models.FloatField()
    credits = models.CharField(max_length = 20000)
    total_credits = models.FloatField(default = 0.)
    booked_dates = models.CharField(max_length = 2000)
