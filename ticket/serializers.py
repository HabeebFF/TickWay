from rest_framework import serializers
from .models import Users, Ticket, Wallet

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number','password', 'is_superuser', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('user_id', 'email', 'username', 'first_name', 'last_name', 'phone_number','password', 'is_superuser', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}
