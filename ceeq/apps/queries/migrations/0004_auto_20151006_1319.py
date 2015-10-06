# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0003_auto_20151006_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='indicator_field',
            field=models.TextField(null=True, blank=True),
        ),
    ]
