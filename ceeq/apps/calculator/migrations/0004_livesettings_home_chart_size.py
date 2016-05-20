# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0003_auto_20150925_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='livesettings',
            name='home_chart_size',
            field=models.IntegerField(default=0),
        ),
    ]
