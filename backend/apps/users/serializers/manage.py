from rest_framework import serializers

from ..models import User


class UserPermissionUpdateSerializer(serializers.Serializer):
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    role_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    workspace_id = serializers.IntegerField(required=False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fio", "is_staff", "is_superuser"]
