"""
Конфигурация тестового приложения для apps/core/.
"""

from django.apps import AppConfig


class TestsCoreConfig(AppConfig):
    """
    Конфигурация тестового приложения.

    Используется для создания тестовых моделей для проверки BaseModel и OwnedModel.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "tests.core"
    label = "tests_core"
    verbose_name = "Tests Core"
