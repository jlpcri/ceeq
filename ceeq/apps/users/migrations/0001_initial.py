# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bug', models.BooleanField(default=True)),
                ('new_feature', models.BooleanField(default=False)),
                ('task', models.BooleanField(default=False)),
                ('improvement', models.BooleanField(default=False)),
                ('suggested_improvement', models.BooleanField(default=False)),
                ('environment', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
