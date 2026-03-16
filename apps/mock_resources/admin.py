from django.contrib import admin

from .models import MockOrder


@admin.register(MockOrder)
class MockOrderAdmin(admin.ModelAdmin):
    """Админка mock-заказов."""

    list_display = ("id", "title", "status", "amount")
    list_filter = ("status",)
    search_fields = ("title",)
