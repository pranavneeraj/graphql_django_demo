# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-28 08:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_auto_20170928_0846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='developer',
        ),
        migrations.AddField(
            model_name='project',
            name='developer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.Developer'),
            preserve_default=False,
        ),
    ]
