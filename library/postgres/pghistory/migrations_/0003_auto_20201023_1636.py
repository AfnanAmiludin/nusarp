# Generated by Django 3.1.2 on 2020-10-23 21:36

from django.db import migrations

import pghistory.models


class Migration(migrations.Migration):
    dependencies = [
        ("pghistory", "0002_aggregateevent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="context",
            name="metadata",
            field=pghistory.models.PGHistoryJSONField(default=dict),
        ),
    ]
