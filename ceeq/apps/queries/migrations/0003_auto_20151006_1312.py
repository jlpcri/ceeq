# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0002_scorehistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='indicator_field',
            field=models.TextField(null=True),
        ),
    ]
