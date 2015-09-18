# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0002_auto_20150915_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='componentcomplexity',
            name='project',
            field=models.ForeignKey(to='queries.Project'),
        ),
        migrations.AlterField(
            model_name='componentimpact',
            name='impact_map',
            field=models.ForeignKey(to='calculator.ImpactMap'),
        ),
        migrations.AlterField(
            model_name='resulthistory',
            name='project',
            field=models.ForeignKey(to='queries.Project'),
        ),
    ]
