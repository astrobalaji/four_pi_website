# Generated by Django 2.2 on 2020-06-25 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obs_review', '0002_auto_20200625_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obs_rev',
            name='accuracy',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='obs_rev',
            name='data_quality',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]