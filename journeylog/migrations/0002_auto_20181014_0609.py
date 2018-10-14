# Generated by Django 2.1 on 2018-10-14 03:09

from django.db import migrations
import separatedvaluesfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('journeylog', '0001_initial_squashed_0003_auto_20181014_0556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalpage',
            name='disabled_modules',
            field=separatedvaluesfield.models.SeparatedValuesField(blank=True, choices=[(1, 'Description'), (2, 'Photos'), (3, 'Map')], max_length=255),
        ),
    ]
