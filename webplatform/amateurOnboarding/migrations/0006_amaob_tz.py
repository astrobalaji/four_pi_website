# Generated by Django 2.2.1 on 2020-02-19 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amateurOnboarding', '0005_auto_20200207_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='amaob',
            name='tz',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]
