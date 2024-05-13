from rest_framework import serializers
from .models import Users

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number','password')
        extra_kwargs = {'password': {'write_only': True}}
