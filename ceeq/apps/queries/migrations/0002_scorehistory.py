# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoreHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now=True, db_index=True)),
                ('access', models.BooleanField(default=False)),
                ('combined_score', django.contrib.postgres.fields.ArrayField(null=True, base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None)),
                ('internal_score', django.contrib.postgres.fields.ArrayField(null=True, base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None)),
                ('uat_score', django.contrib.postgres.fields.ArrayField(null=True, base_field=models.DecimalField(default=0, max_digits=10, decimal_places=2), size=None)),
                ('project', models.ForeignKey(to='queries.Project')),
            ],
        ),
    ]
