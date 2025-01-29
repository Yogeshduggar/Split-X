from rest_framework import serializers
from .models import User, Transaction, Settlement,Group

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'category', 'type', 'created_at']

class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = ['id', 'group', 'message', 'status', 'user_to_pay', 'user_to_be_paid', 'amount', 'created_at']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'user_admin', 'users', 'created_at', 'updated_at']