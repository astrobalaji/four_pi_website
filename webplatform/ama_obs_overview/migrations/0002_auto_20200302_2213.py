# Generated by Django 2.2.1 on 2020-03-02 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ama_obs_overview', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file_details',
            name='bias_names',
        ),
        migrations.RemoveField(
            model_name='file_details',
            name='darks_names',
        ),
        migrations.RemoveField(
            model_name='file_details',
            name='flats_names',
        ),
        migrations.RemoveField(
            model_name='file_details',
            name='lights_names',
        ),
        migrations.RemoveField(
            model_name='file_details',
            name='obs_comments',
        ),
        migrations.AddField(
            model_name='file_details',
            name='filename',
            field=models.CharField(default='', max_length=2000),
            preserve_default=False,
        ),
    ]