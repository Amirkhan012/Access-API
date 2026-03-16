from django.db import models


class MockOrder(models.Model):
    """Хранит простой mock-заказ."""

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=100, default="new")
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        """Возвращает короткое имя заказа."""
        return self.title
