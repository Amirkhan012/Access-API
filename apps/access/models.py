from django.conf import settings
from django.db import models


class Role(models.Model):
    """Хранит пользовательскую роль."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        """Возвращает название роли."""
        return self.name


class Resource(models.Model):
    """Хранит защищаемый ресурс."""

    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        """Возвращает код ресурса."""
        return self.code


class Action(models.Model):
    """Хранит действие, разрешённое над ресурсом."""

    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        """Возвращает код действия."""
        return self.code


class UserRole(models.Model):
    """Связывает пользователя с ролью."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                name="unique_user_role",
            ),
        ]

    def __str__(self) -> str:
        """Возвращает читаемое представление назначения роли."""
        return f"{self.user.email} -> {self.role.name}"


class RolePermission(models.Model):
    """Связывает роль с действием над ресурсом."""

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    action = models.ForeignKey(
        Action,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["role", "resource", "action"],
                name="unique_role_resource_action",
            ),
        ]

    def __str__(self) -> str:
        """Возвращает читаемое представление правила доступа."""
        return f"{self.role.name} -> {self.resource.code}:{self.action.code}"
