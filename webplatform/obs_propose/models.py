from django.db import models
import datetime

# Create your models here.
class Obs_Prop(models.Model):
    obs_title = models.CharField(max_length=200)
    obs_type = models.CharField(max_length=200)
    field_type = models.CharField(max_length=200)
    coords_ra = models.CharField(max_length=200)
    coords_dec = models.CharField(max_length=200)
    fov = models.FloatField()
    magnitude = models.FloatField()
    desired_exposure = models.FloatField()
    description = models.CharField(max_length=2000)
    settings = models.CharField(max_length=2000)
    user_id = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    submitted_on = models.DateField(default=datetime.date.today)
    selected_users = models.CharField(max_length=2000)
    unselected_users = models.CharField(max_length=2000)
    requested_users = models.CharField(max_length=2000)
    accepted_users = models.CharField(max_length=2000)
    completed_users = models.CharField(max_length=2000)
