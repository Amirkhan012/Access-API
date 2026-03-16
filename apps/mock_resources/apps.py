from django.apps import AppConfig


class MockResourcesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mock_resources"
    label = "mock_resources"
