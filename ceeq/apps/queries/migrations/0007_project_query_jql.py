# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0006_auto_20160418_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='query_jql',
            field=models.TextField(null=True, blank=True),
        ),
    ]
