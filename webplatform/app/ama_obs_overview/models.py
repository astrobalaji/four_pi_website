from django.db import models

# Create your models here.
class FileUpload(models.Model):
    data = models.FileField(upload_to = 'data_files/')

class File_Details(models.Model):
    filename = models.CharField(max_length = 2000)
    prof_id = models.CharField(max_length = 200)
    obs_id = models.IntegerField()
    ama_id = models.CharField(max_length = 300)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    sorted = models.BooleanField(default=False)
