# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='juicegroupnames',
            table='juice_groupnames',
        ),
        migrations.AlterModelTable(
            name='juicegroupvm',
            table='juice_groupvm',
        ),
    ]
