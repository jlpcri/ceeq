# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0004_auto_20151006_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scorehistory',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
