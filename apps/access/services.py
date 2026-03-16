from apps.users.models import User

from .models import RolePermission


def has_permission(
    *,
    user: User,
    resource_code: str,
    action_code: str,
) -> bool:
    """Проверяет доступ пользователя к действию над ресурсом."""
    if not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    return RolePermission.objects.filter(
        role__user_roles__user=user,
        resource__code=resource_code,
        action__code=action_code,
    ).exists()


def can_manage_access(*, user: User) -> bool:
    """Проверяет, может ли пользователь управлять правилами доступа."""
    if not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    if user.is_superuser:
        return True

    return has_permission(
        user=user,
        resource_code="access_rules",
        action_code="manage",
    )
