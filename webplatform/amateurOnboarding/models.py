from django.db import models

# Create your models here.
class AmaOB(models.Model):
    location = models.CharField(max_length=200)
    lat = models.FloatField()
    lon = models.FloatField()
    avail = models.BooleanField()
    telescope_aper = models.FloatField()
    telescope_flength = models.FloatField()
    det_mod = models.CharField(max_length=200)
    det_pix_scale = models.FloatField()
    detector_dimensions = models.CharField(max_length=200)
    user_id = models.CharField(max_length=200)
    fov = models.FloatField()
