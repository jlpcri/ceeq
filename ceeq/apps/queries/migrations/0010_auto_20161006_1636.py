# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0009_auto_20160906_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='resolution_blacklist',
            field=django.contrib.postgres.fields.ArrayField(default=[b'Duplicate', b'Works as Designed', b'Working as Required'], base_field=models.CharField(max_length=50, blank=True), size=None),
        ),
    ]
