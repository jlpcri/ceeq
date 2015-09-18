# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0005_auto_20150917_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resulthistory',
            name='combined_testing_table',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='internal_testing_table',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='score_by_component',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='uat_testing_table',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True),
        ),
    ]
