# Generated by Django 4.2.6 on 2024-05-12 23:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ticket", "0005_rename_tickets_ticket"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ticket",
            old_name="day",
            new_name="transport_date",
        ),
        migrations.AddField(
            model_name="ticket",
            name="booking_date",
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name="ticket",
            name="price",
            field=models.IntegerField(default=50),
        ),
    ]
