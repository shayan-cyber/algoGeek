# Generated by Django 3.2.4 on 2021-06-12 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sub_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='status',
            field=models.CharField(choices=[('AC', 'Active'), ('IA', 'Inactive')], default='AC', max_length=2),
        ),
    ]