# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentComplexity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('component_name', models.TextField()),
                ('complexity', models.IntegerField(default=0)),
                ('project', models.ForeignKey(to='projects.Project')),
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
                ('created', models.DateTimeField(auto_now=True, db_index=True)),
                ('confirmed', models.DateTimeField(db_index=True)),
                ('scored', models.BooleanField(default=False)),
                ('internal_score', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('uat_score', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('overall_score', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='ResultTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
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
        migrations.AddField(
            model_name='resulthistory',
            name='combined_testing_table',
            field=models.ForeignKey(related_name='combined_testing', to='calculator.ResultTable'),
        ),
        migrations.AddField(
            model_name='resulthistory',
            name='internal_testing_table',
            field=models.ForeignKey(related_name='internal_testing', to='calculator.ResultTable'),
        ),
        migrations.AddField(
            model_name='resulthistory',
            name='project',
            field=models.ForeignKey(to='projects.Project'),
        ),
        migrations.AddField(
            model_name='resulthistory',
            name='uat_testing_table',
            field=models.ForeignKey(related_name='uat_testing', to='calculator.ResultTable'),
        ),
        migrations.AddField(
            model_name='componentimpact',
            name='impact_map',
            field=models.ForeignKey(to='calculator.ImpactMap'),
        ),
        migrations.AlterUniqueTogether(
            name='componentimpact',
            unique_together=set([('impact_map', 'component_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='componentcomplexity',
            unique_together=set([('project', 'component_name')]),
        ),
    ]
