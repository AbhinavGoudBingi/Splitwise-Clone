# Generated by Django 2.2.6 on 2019-11-25 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_auto_20191125_0216'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouptable',
            name='checkmember',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='grouptrans',
            name='checkmember',
            field=models.BooleanField(default=True),
        ),
    ]
