# Generated by Django 2.2 on 2020-03-19 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obs_propose', '0013_obs_prop_rejected_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='obs_prop',
            name='exp_max',
        ),
        migrations.RemoveField(
            model_name='obs_prop',
            name='exp_min',
        ),
        migrations.AddField(
            model_name='obs_prop',
            name='min_snr',
            field=models.FloatField(default=10.0),
            preserve_default=False,
        ),
    ]
