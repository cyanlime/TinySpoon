# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-15 18:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('childrenrecipe', '0005_auto_20161115_1744'),
    ]

    operations = [
        migrations.RenameField(
            model_name='weekrecommend',
            old_name='subtitle',
            new_name='headline',
        ),
        migrations.RenameField(
            model_name='weekrecommend',
            old_name='title',
            new_name='subhead',
        ),
    ]