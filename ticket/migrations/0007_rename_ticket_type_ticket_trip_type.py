# Generated by Django 4.2.6 on 2024-05-12 23:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "ticket",
            "0006_rename_day_ticket_transport_date_ticket_booking_date_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="ticket",
            old_name="ticket_type",
            new_name="trip_type",
        ),
    ]