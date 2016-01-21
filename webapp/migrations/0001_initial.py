# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JuiceGroupnames',
            fields=[
                ('id', models.IntegerField(primary_key=True, unique=True, serialize=False)),
                ('name', models.TextField()),
            ],
            options={
                'managed': False,
                'db_table': 'JuiceGroupnames',
            },
        ),
        migrations.CreateModel(
            name='JuiceGroupvm',
            fields=[
                ('id', models.IntegerField(primary_key=True, unique=True, serialize=False)),
                ('vmid', models.TextField()),
                ('groupid', models.TextField()),
            ],
            options={
                'managed': False,
                'db_table': 'JuiceGroupvm',
            },
        ),
    ]
