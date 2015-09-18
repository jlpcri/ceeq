# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0003_auto_20150915_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resulthistory',
            name='combined_testing_table',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, null=True), size=None), size=None),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='internal_testing_table',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, null=True), size=None), size=None),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='uat_testing_table',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, null=True), size=None), size=None),
        ),
    ]
