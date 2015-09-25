# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        HStoreExtension(),

        migrations.CreateModel(
            name='ComponentComplexity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_name', models.TextField()),
                ('complexity', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['project', 'component_name'],
            },
        ),
        migrations.CreateModel(
            name='ComponentImpact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_name', models.TextField()),
                ('impact', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
            ],
            options={
                'ordering': ['impact_map', 'component_name'],
            },
        ),
        migrations.CreateModel(
            name='ImpactMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LiveSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score_scalar', models.IntegerField(default=0)),
                ('current_delay', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ResultHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('confirmed', models.DateTimeField(auto_now=True, db_index=True)),
                ('query_results', django.contrib.postgres.fields.ArrayField(size=None, base_field=django.contrib.postgres.fields.hstore.HStoreField(), blank=True)),
                ('scored', models.BooleanField(default=False)),
                ('internal_testing_table', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None)),
                ('uat_testing_table', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None)),
                ('combined_testing_table', django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None)),
                ('score_by_component', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20, blank=True), size=None), blank=True)),
                ('internal_score', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('uat_score', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('overall_score', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='SeverityMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('blocker', models.IntegerField(default=0)),
                ('critical', models.IntegerField(default=0)),
                ('major', models.IntegerField(default=0)),
                ('minor', models.IntegerField(default=0)),
                ('trivial', models.IntegerField(default=0)),
            ],
        ),
    ]
