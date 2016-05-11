# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0004_livesettings_home_chart_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='livesettings',
            name='issue_status_closed',
            field=django.contrib.postgres.fields.ArrayField(default=[b'Closed', b'COMPLETE'], base_field=models.CharField(max_length=30, blank=True), size=None),
        ),
        migrations.AddField(
            model_name='livesettings',
            name='issue_status_open',
            field=django.contrib.postgres.fields.ArrayField(default=[b'Open', b'In Progress', b'Reopened', b'Discovery', b'Review', b'Pending', b'Research', b'Pending Estimate'], base_field=models.CharField(max_length=30, blank=True), size=None),
        ),
        migrations.AddField(
            model_name='livesettings',
            name='issue_status_resolved',
            field=django.contrib.postgres.fields.ArrayField(default=[b'Resolved', b'UAT Testing', b'Done'], base_field=models.CharField(max_length=30, blank=True), size=None),
        ),
    ]
