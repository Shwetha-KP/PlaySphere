# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2023-07-14 12:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gameview', '0004_auto_20230714_1755'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratings',
            name='player',
        ),
        migrations.DeleteModel(
            name='ratings',
        ),
    ]
