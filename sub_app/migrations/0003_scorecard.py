# Generated by Django 3.2.4 on 2021-06-12 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sub_app', '0002_contest_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoreCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('_contest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sub_app.contest')),
                ('prof', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sub_app.profile')),
            ],
        ),
    ]