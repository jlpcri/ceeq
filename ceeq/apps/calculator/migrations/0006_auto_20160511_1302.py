# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0005_auto_20160511_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livesettings',
            name='issue_status_closed',
            field=django.contrib.postgres.fields.ArrayField(default=[b'Closed', b'Complete'], base_field=models.CharField(max_length=30, blank=True), size=None),
        ),
    ]
