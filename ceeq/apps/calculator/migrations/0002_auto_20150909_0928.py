# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0001_initial'),
    ]

    operations = [
        HStoreExtension(),

        migrations.AddField(
            model_name='resulthistory',
            name='query_results',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=django.contrib.postgres.fields.hstore.HStoreField(), size=None),
        ),
        migrations.AddField(
            model_name='resulthistory',
            name='score_by_component',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True),
        ),
        migrations.AddField(
            model_name='resulttable',
            name='data',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None), size=None),
        ),
        migrations.AlterField(
            model_name='componentcomplexity',
            name='project',
            field=models.ForeignKey(to='queries.Project'),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='project',
            field=models.ForeignKey(to='queries.Project'),
        ),
    ]
