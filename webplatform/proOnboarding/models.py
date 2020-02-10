from django.db import models

# Create your models here.

class proOB(models.Model):
    affiliation = models.CharField(max_length = 200)
    field_of_interest = models.CharField(max_length = 200)
    user_id = models.CharField(max_length=200)
