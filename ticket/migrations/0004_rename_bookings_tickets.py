# Generated by Django 4.2.6 on 2024-05-12 22:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ticket", "0003_bookings"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Bookings",
            new_name="Tickets",
        ),
    ]
