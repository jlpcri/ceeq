# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0002_auto_20150924_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resulthistory',
            name='combined_testing_table',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='internal_testing_table',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='uat_testing_table',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None),
        ),
    ]
