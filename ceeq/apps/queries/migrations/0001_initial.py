# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0002_auto_20150909_0928'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('jira_user', models.TextField()),
                ('password', models.TextField()),
                ('indicator_field', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('jira_key', models.CharField(max_length=16)),
                ('jira_version', models.TextField()),
                ('issue_types', django.contrib.postgres.fields.ArrayField(default=b'Bug', base_field=models.CharField(max_length=50, blank=True), size=None)),
                ('resolution_blacklist', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50, blank=True), size=None)),
                ('component_field', models.IntegerField()),
                ('impact_map', models.ForeignKey(to='calculator.ImpactMap')),
                ('instance', models.ForeignKey(to='queries.Instance')),
            ],
        ),
    ]
