from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

# Create your models here.

class Users(AbstractUser):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=40, null=False)
    email = models.EmailField(unique=True, null=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=11)
    password = models.CharField(max_length=120, null=False)


class Wallet(models.Model):
    wallet_id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    wallet_balance = models.DecimalField(default=5000, null=False, decimal_places=2, max_digits=10)


class Ticket(models.Model):
    ticket_id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    trip_type = models.CharField(max_length=10)
    from_loc = models.CharField(max_length=40)
    to_loc = models.CharField(max_length=40)
    booking_date = models.DateTimeField(default=datetime.datetime.now)
    transport_date = models.DateField()
    return_date = models.DateField(default=None, null=True)
    number_of_tickets = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=5)


class Location(models.Model):
    location_id = models.IntegerField(primary_key=True)
    loc_name = models.CharField(max_length=20)


class Transaction(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    transaction_type = models.CharField(max_length=6)
    transaction_status = models.CharField(max_length=10)
    access_code = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    