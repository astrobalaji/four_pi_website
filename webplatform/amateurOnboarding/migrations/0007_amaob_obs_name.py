# Generated by Django 2.2.1 on 2020-02-21 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amateurOnboarding', '0006_amaob_tz'),
    ]

    operations = [
        migrations.AddField(
            model_name='amaob',
            name='obs_name',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
