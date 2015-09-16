# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0002_auto_20150915_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='jira_fields',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=models.CharField(default=b'', max_length=50), size=None),
        ),
    ]
