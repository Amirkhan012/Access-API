from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils import timezone

from .models import UserSession

User = get_user_model()

SESSION_LIFETIME_DAYS: int = 7


def get_client_ip(request: HttpRequest) -> str | None:
    """Возвращает IP-адрес клиента."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def assign_default_role(*, user: User) -> None:
    """Создаёт базовую роль viewer и назначает её пользователю."""
    from apps.access.models import Role, UserRole

    viewer_role, _ = Role.objects.get_or_create(
        name="viewer",
        defaults={"description": "Базовая роль по умолчанию."},
    )
    UserRole.objects.get_or_create(user=user, role=viewer_role)


def register_user(*, validated_data: dict[str, Any]) -> User:
    """Создаёт пользователя и назначает базовую роль."""
    password = validated_data.pop("password")
    validated_data.pop("password_repeat", None)

    user = User.objects.create_user(
        password=password,
        **validated_data,
    )
    assign_default_role(user=user)
    return user


def authenticate_user(*, email: str, password: str) -> User | None:
    """Проверяет email и пароль и возвращает пользователя."""
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None

    if not user.is_active:
        return None

    if not user.check_password(password):
        return None

    return user


def create_user_session(
    *,
    user: User,
    ip_address: str | None,
    user_agent: str,
) -> UserSession:
    """Создаёт новую активную сессию пользователя."""
    return UserSession.objects.create(
        user=user,
        session_key=UserSession.generate_session_key(),
        expires_at=timezone.now() + timedelta(days=SESSION_LIFETIME_DAYS),
        ip_address=ip_address,
        user_agent=user_agent[:255],
    )


def get_active_session(*, session_key: str) -> UserSession | None:
    """Возвращает активную сессию по её ключу."""
    try:
        session = UserSession.objects.select_related("user").get(
            session_key=session_key,
            is_active=True,
        )
    except UserSession.DoesNotExist:
        return None

    now = timezone.now()

    if session.expires_at <= now:
        session.is_active = False
        session.last_activity_at = now
        session.save(
            update_fields=["is_active", "last_activity_at", "updated_at"]
        )
        return None

    if not session.user.is_active:
        session.is_active = False
        session.last_activity_at = now
        session.save(
            update_fields=["is_active", "last_activity_at", "updated_at"]
        )
        return None

    return session


def touch_session(*, session: UserSession) -> None:
    """Обновляет время последней активности сессии."""
    session.last_activity_at = timezone.now()
    session.save(update_fields=["last_activity_at", "updated_at"])


def deactivate_session(*, session: UserSession | None) -> None:
    """Деактивирует одну сессию."""
    if session is None:
        return

    session.is_active = False
    session.last_activity_at = timezone.now()
    session.save(update_fields=["is_active", "last_activity_at", "updated_at"])


def deactivate_all_user_sessions(*, user: User) -> None:
    """Деактивирует все активные сессии пользователя."""
    now = timezone.now()
    UserSession.objects.filter(user=user, is_active=True).update(
        is_active=False,
        last_activity_at=now,
        updated_at=now,
    )


def soft_delete_user(*, user: User) -> None:
    """Деактивирует пользователя и все его сессии."""
    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])
    deactivate_all_user_sessions(user=user)
