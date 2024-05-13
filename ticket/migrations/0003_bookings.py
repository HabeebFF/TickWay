# Generated by Django 4.2.6 on 2024-05-12 21:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ticket", "0002_alter_users_first_name_alter_users_last_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bookings",
            fields=[
                ("ticket_id", models.IntegerField(primary_key=True, serialize=False)),
                ("ticket_type", models.CharField(max_length=10)),
                ("from_loc", models.CharField(max_length=40)),
                ("to_loc", models.CharField(max_length=40)),
                ("day", models.DateField()),
                ("number_of_tickets", models.IntegerField()),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]