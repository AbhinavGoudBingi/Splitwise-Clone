# Generated by Django 2.2.6 on 2019-11-06 21:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20191106_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='Date',
            field=models.DateTimeField(default=datetime.datetime(2019, 11, 6, 21, 29, 36, 696255), verbose_name='date published'),
        ),
    ]
