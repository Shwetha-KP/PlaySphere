# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2023-07-14 12:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameview', '0003_ratings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratings',
            name='game',
            field=models.TextField(),
        ),
    ]