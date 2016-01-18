# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0006_auto_20160118_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='component_field',
            field=models.TextField(default=b'1', choices=[(b'1', b'CEEQ Components'), (b'2', b'CEEQ Indicator')]),
        ),
    ]
