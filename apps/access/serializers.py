from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Action, Resource, Role, RolePermission, UserRole

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    """Сериализует роли."""

    class Meta:
        model = Role
        fields = ("id", "name", "description")


class ResourceSerializer(serializers.ModelSerializer):
    """Сериализует ресурсы."""

    class Meta:
        model = Resource
        fields = ("id", "code", "name", "description")


class ActionSerializer(serializers.ModelSerializer):
    """Сериализует действия."""

    class Meta:
        model = Action
        fields = ("id", "code", "name", "description")


class UserRoleReadSerializer(serializers.ModelSerializer):
    """Сериализует назначения ролей пользователям для чтения."""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = UserRole
        fields = (
            "id", "user", "user_email",
            "role", "role_name", "assigned_at"
        )


class UserRoleWriteSerializer(serializers.ModelSerializer):
    """Сериализует назначения ролей пользователям для создания."""

    class Meta:
        model = UserRole
        fields = ("id", "user", "role")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Запрещает дублирующие назначения ролей."""
        user = attrs["user"]
        role = attrs["role"]

        if UserRole.objects.filter(user=user, role=role).exists():
            raise serializers.ValidationError(
                {"detail": "У пользователя уже есть эта роль."}
            )

        return attrs


class RolePermissionReadSerializer(serializers.ModelSerializer):
    """Сериализует правила доступа ролей для чтения."""

    role_name = serializers.CharField(
        source="role.name", read_only=True)
    resource_code = serializers.CharField(
        source="resource.code", read_only=True)
    action_code = serializers.CharField(
        source="action.code", read_only=True)

    class Meta:
        model = RolePermission
        fields = (
            "id",
            "role",
            "role_name",
            "resource",
            "resource_code",
            "action",
            "action_code",
            "created_at",
        )


class RolePermissionWriteSerializer(serializers.ModelSerializer):
    """Сериализует правила доступа ролей для создания."""

    class Meta:
        model = RolePermission
        fields = ("id", "role", "resource", "action")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Запрещает дублирующие правила доступа."""
        role = attrs["role"]
        resource = attrs["resource"]
        action = attrs["action"]

        if RolePermission.objects.filter(
            role=role,
            resource=resource,
            action=action,
        ).exists():
            raise serializers.ValidationError(
                {"detail": "Такое правило доступа уже существует."}
            )

        return attrs
