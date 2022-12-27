# Generated by Django 2.2 on 2020-06-27 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obs_review', '0004_auto_20200626_0926'),
    ]

    operations = [
        migrations.RenameField(
            model_name='obs_rev',
            old_name='data_quality',
            new_name='instructs_follow',
        ),
        migrations.AddField(
            model_name='obs_rev',
            name='quality_calib',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='obs_rev',
            name='snr',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]