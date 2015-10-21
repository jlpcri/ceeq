# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FrameworkParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parameter', models.CharField(unique=True, max_length=200)),
                ('value', models.DecimalField(default=0, max_digits=3, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('jira_name', models.CharField(max_length=200)),
                ('jira_version', models.CharField(default=b'All Versions', max_length=200)),
                ('score', models.DecimalField(default=109, max_digits=5, decimal_places=2)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'date added')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name=b'date modified')),
                ('active', models.BooleanField(default=True)),
                ('complete', models.BooleanField(default=False)),
                ('accuracy', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('suitability', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('interoperability', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('functional_security', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('usability', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('accessibility', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('technical_security', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('reliability', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('efficiency', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('maintainability', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('portability', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
            ],
        ),
        migrations.CreateModel(
            name='ProjectComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=50)),
                ('weight', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectComponentsDefectsDensity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=200)),
                ('created', models.DateField(auto_now_add=True)),
                ('ceeq', models.DecimalField(default=0, max_digits=5, decimal_places=3)),
                ('ceeq_closed', models.DecimalField(default=10, max_digits=5, decimal_places=3)),
                ('cxp', models.DecimalField(default=0, max_digits=5, decimal_places=3)),
                ('platform', models.DecimalField(default=0, max_digits=5, decimal_places=3)),
                ('reports', models.DecimalField(default=0, max_digits=5, decimal_places=3)),
                ('application', models.DecimalField(default=0, max_digits=5, decimal_places=3)),
                ('voice_slots', models.DecimalField(default=0, max_digits=5, decimal_places=3)),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
            options={
                'ordering': ['created', 'version'],
            },
        ),
        migrations.CreateModel(
            name='ProjectType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', unique=True, max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='projectcomponent',
            name='project_type',
            field=models.ForeignKey(to='projects.ProjectType'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.ForeignKey(default=1, to='projects.ProjectType'),
        ),
        migrations.AlterUniqueTogether(
            name='projectcomponent',
            unique_together=set([('project_type', 'name', 'weight')]),
        ),
    ]
