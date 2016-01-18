# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0005_auto_20151007_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='component_field',
            field=models.TextField(default=b'1', choices=[(b'1', b'1'), (b'2', b'2')]),
        ),
    ]
