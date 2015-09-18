# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0004_auto_20150917_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resulthistory',
            name='combined_testing_table',
            field=django.contrib.postgres.fields.ArrayField(size=None, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='internal_testing_table',
            field=django.contrib.postgres.fields.ArrayField(size=None, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='query_results',
            field=django.contrib.postgres.fields.ArrayField(size=None, base_field=django.contrib.postgres.fields.hstore.HStoreField(), blank=True),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='score_by_component',
            field=django.contrib.postgres.fields.ArrayField(size=None, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='uat_testing_table',
            field=django.contrib.postgres.fields.ArrayField(size=None, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True),
        ),
    ]
