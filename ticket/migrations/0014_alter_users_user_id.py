# Generated by Django 4.2.6 on 2024-05-28 23:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ticket", "0013_remove_ticket_number_of_tickets_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="users",
            name="user_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
