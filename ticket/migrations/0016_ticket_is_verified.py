# Generated by Django 4.2.6 on 2024-05-29 16:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ticket", "0015_alter_location_location_id_alter_ticket_ticket_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
    ]
