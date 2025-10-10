"""
Общие fixtures для всех тестов проекта.

Настройка pytest-django и переиспользуемые fixtures.
"""

import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    """
    Fixture для создания обычного пользователя.

    Args:
        db: pytest-django fixture для доступа к БД

    Returns:
        User: Созданный пользователь
    """
    User = get_user_model()
    user = User.objects.create_user(
        username="testuser",
        email="user@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User",
    )
    user.is_email_verified = True
    user.save()
    return user


@pytest.fixture
def another_user(db):
    """
    Fixture для создания другого пользователя (для тестов прав доступа).

    Args:
        db: pytest-django fixture для доступа к БД

    Returns:
        User: Созданный пользователь
    """
    User = get_user_model()
    user = User.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password="testpassword123",
        first_name="Another",
        last_name="User",
    )
    user.is_email_verified = True
    user.save()
    return user


@pytest.fixture
def manager_user(db):
    """
    Fixture для создания пользователя-менеджера.

    Args:
        db: pytest-django fixture для доступа к БД

    Returns:
        User: Менеджер с правами is_staff
    """
    User = get_user_model()
    user = User.objects.create_user(
        username="manager",
        email="manager@example.com",
        password="testpassword123",
        first_name="Manager",
        last_name="User",
    )
    user.is_staff = True
    user.is_email_verified = True
    user.save()
    return user
