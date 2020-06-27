from django.db import models


# Create your models here.
class obs_rev(models.Model):
    obs_title = models.CharField(max_length=200)
    prop_title = models.CharField(max_length=200)
    prop_pk = models.IntegerField()
    obs_id = models.CharField(max_length=200)
    snr = models.IntegerField()
    accuracy = models.IntegerField()
    quality_calib = models.IntegerField()
    instructs_follow = models.IntegerField()
    review = models.CharField(max_length=2000)
    posted_at = models.DateTimeField(auto_now_add=True)
    #prof_name = models.CharField(max_length = 2000)
