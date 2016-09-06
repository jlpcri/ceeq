# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0008_auto_20160513_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='issue_types',
            field=django.contrib.postgres.fields.ArrayField(default=[b'Bug', b'Bug task', b'Bug (QA)', b'Bug (UAT)'], base_field=models.CharField(max_length=50, blank=True), size=None),
        ),
    ]
