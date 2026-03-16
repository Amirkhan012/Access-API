from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализует профиль пользователя."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "full_name",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("id", "is_active", "date_joined", "full_name")


class RegisterSerializer(serializers.ModelSerializer):
    """Проверяет данные для регистрации."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_repeat = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "password",
            "password_repeat",
        )

    def validate_email(self, value: str) -> str:
        """Проверяет, что email ещё не занят."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Проверяет совпадение паролей."""
        if attrs["password"] != attrs["password_repeat"]:
            raise serializers.ValidationError(
                {"password_repeat": "Пароли не совпадают."}
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    """Проверяет данные для входа."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
