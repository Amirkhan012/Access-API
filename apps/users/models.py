import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с email в качестве логина."""

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name"]

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        """Возвращает email пользователя."""
        return self.email

    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя в удобном виде."""
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()


class UserSession(models.Model):
    """Хранит пользовательские сессии для cookie-аутентификации."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    session_key = models.CharField(max_length=128, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    expires_at = models.DateTimeField()
    last_activity_at = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Возвращает короткое представление сессии."""
        return f"{self.user.email} | {self.session_key[:12]}"

    @staticmethod
    def generate_session_key() -> str:
        """Генерирует криптостойкий ключ сессии."""
        return secrets.token_urlsafe(32)
