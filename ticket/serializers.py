from rest_framework import serializers
from .models import Users, Ticket

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number','password', 'is_superuser', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'