from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from ..models import User


class LogSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email и пароль обязательны.")

        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Неверные учетные данные.")

        attrs["user"] = user
        return attrs


class RegSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6)

    class Meta:
        model = User
        fields = ["email", "password", "fio"]

    def save(self, **kwargs):
        user = User()
        user.email = self.validated_data["email"]
        user.fio = self.validated_data["fio"]
        user.set_password(self.validated_data["password"])
        user.save()
        Token.objects.create(user=user)
        return user
