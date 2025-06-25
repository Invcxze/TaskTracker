from rest_framework import serializers
from ..models import User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fio", "is_active", "is_staff"]
