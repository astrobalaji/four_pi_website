# Generated by Django 2.2.1 on 2020-03-12 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amateurOnboarding', '0014_auto_20200304_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='amaob',
            name='QE',
            field=models.FloatField(default=100.0, null=True),
        ),
    ]
