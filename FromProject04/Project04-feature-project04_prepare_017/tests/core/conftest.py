"""
Fixtures для тестирования apps/core/.
"""

import pytest

from .models import OwnedItem, SimpleModel


@pytest.fixture
def simple_model_instance(db):
    """
    Fixture для создания экземпляра SimpleModel.

    Returns:
        SimpleModel: Созданный объект
    """
    return SimpleModel.objects.create(name="Test Object")


@pytest.fixture
def owned_item(db, user):
    """
    Fixture для создания экземпляра OwnedItem с владельцем.

    Args:
        user: Пользователь-владелец из общего conftest.py

    Returns:
        OwnedItem: Созданный объект с владельцем
    """
    return OwnedItem.objects.create(owner=user, title="Test Item", description="Test Description")
