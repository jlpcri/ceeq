# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0005_auto_20151007_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='query_field',
            field=models.CharField(default=b'Project Version', max_length=20, choices=[(b'JQL Query', b'JQL Query'), (b'Project Version', b'Project Version')]),
        ),
        migrations.AlterField(
            model_name='project',
            name='component_field',
            field=models.IntegerField(default=1, choices=[(1, b'CEEQ Components'), (2, b'CEEQ Indicator')]),
        ),
    ]
