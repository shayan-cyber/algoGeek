# Generated by Django 3.2.4 on 2021-06-14 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sub_app', '0007_scorecard_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='total_points',
            field=models.IntegerField(default=0),
        ),
    ]
