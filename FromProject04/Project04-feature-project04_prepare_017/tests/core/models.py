"""
Тестовые модели для apps/core/.

Конкретные модели для тестирования абстрактных BaseModel и OwnedModel.
"""

from django.db import models

from apps.core.models import BaseModel, OwnedModel


class SimpleModel(BaseModel):
    """
    Конкретная модель для тестирования BaseModel.

    Наследует только от BaseModel для проверки базового функционала.
    """

    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests_core"
        ordering = ["-created_at"]


class OwnedItem(OwnedModel):
    """
    Конкретная модель для тестирования OwnedModel.

    Наследует от OwnedModel для проверки функционала с владельцем.
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        app_label = "tests_core"
        ordering = ["-created_at"]
