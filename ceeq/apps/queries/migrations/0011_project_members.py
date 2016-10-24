# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('queries', '0010_auto_20161006_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='members',
            field=models.ManyToManyField(to='users.UserSettings', blank=True),
        ),
    ]
