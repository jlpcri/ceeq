# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0001_initial'),
        ('calculator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentcomplexity',
            name='project',
            field=models.ForeignKey(default=1, to='queries.Project'),
        ),
        migrations.AddField(
            model_name='componentimpact',
            name='impact_map',
            field=models.ForeignKey(default=1, to='calculator.ImpactMap'),
        ),
        migrations.AddField(
            model_name='resulthistory',
            name='project',
            field=models.ForeignKey(default=1, to='queries.Project'),
        ),
        migrations.AlterUniqueTogether(
            name='componentcomplexity',
            unique_together=set([('project', 'component_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='componentimpact',
            unique_together=set([('impact_map', 'component_name')]),
        ),
    ]
