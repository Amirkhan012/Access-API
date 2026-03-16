from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для кастомной модели пользователя."""

    ordering = ("id",)
    list_display = ("id", "email", "is_active", "is_staff")
    list_filter = ("is_active",)
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личные данные",
            {"fields": ("first_name", "last_name", "middle_name")},
        ),
        (
            "Права",
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    readonly_fields = ("last_login", "date_joined")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Админка пользовательских сессий."""

    list_display = ("id", "user", "is_active", "expires_at")
    list_filter = ("is_active",)
    search_fields = ("user__email",)
    readonly_fields = ("session_key",)
