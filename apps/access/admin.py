from django.contrib import admin

from .models import Action, Resource, Role, RolePermission, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Админка ролей."""

    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Админка ресурсов."""

    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    """Админка действий."""

    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Админка назначений ролей пользователям."""

    list_display = ("id", "user", "role", "assigned_at")
    list_filter = ("role",)
    search_fields = ("user__email", "role__name")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Админка правил доступа ролей."""

    list_display = ("id", "role", "resource", "action", "created_at")
    list_filter = ("role", "resource", "action")
    search_fields = ("role__name", "resource__code", "action__code")
