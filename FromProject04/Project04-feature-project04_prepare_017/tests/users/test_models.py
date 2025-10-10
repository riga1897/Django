"""
Тесты для моделей приложения users.

Проверяем:
- User model
- UserManager
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class TestUser:
    """Тесты для модели User"""

    @pytest.mark.django_db
    def test_create_user_with_email(self):
        """Проверка: создание пользователя с email"""
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    @pytest.mark.django_db
    def test_create_user_auto_generates_username(self):
        """Проверка: username автоматически генерируется из email (полный email)"""
        user = User.objects.create_user(email="john@example.com", password="pass")

        assert user.username == "john@example.com"

    @pytest.mark.django_db
    def test_create_user_with_custom_username(self):
        """Проверка: можно указать кастомный username"""
        user = User.objects.create_user(email="test@example.com", password="pass", username="custom_user")

        assert user.username == "custom_user"

    @pytest.mark.django_db
    def test_create_user_without_email_raises_error(self):
        """Проверка: создание пользователя без email вызывает ошибку"""
        with pytest.raises(ValueError, match="Email обязателен"):
            User.objects.create_user(email="", password="pass")

    @pytest.mark.django_db
    def test_email_is_unique(self):
        """Проверка: email должен быть уникальным"""
        User.objects.create_user(email="test@example.com", password="pass")

        with pytest.raises(IntegrityError):
            User.objects.create_user(email="test@example.com", password="pass2")

    @pytest.mark.django_db
    def test_create_superuser(self):
        """Проверка: создание суперпользователя"""
        user = User.objects.create_superuser(email="admin@example.com", password="adminpass")

        assert user.email == "admin@example.com"
        assert user.is_staff is True
        assert user.is_superuser is True

    @pytest.mark.django_db
    def test_create_superuser_without_staff_raises_error(self):
        """Проверка: суперпользователь должен иметь is_staff=True"""
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            User.objects.create_superuser(email="admin@example.com", password="pass", is_staff=False)

    @pytest.mark.django_db
    def test_create_superuser_without_superuser_raises_error(self):
        """Проверка: суперпользователь должен иметь is_superuser=True"""
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
            User.objects.create_superuser(email="admin@example.com", password="pass", is_superuser=False)

    @pytest.mark.django_db
    def test_user_str_returns_email(self):
        """Проверка: __str__ возвращает email"""
        user = User.objects.create_user(email="test@example.com", password="pass")

        assert str(user) == "test@example.com"

    @pytest.mark.django_db
    def test_get_full_name_with_names(self):
        """Проверка: get_full_name() возвращает полное имя"""
        user = User.objects.create_user(email="test@example.com", password="pass", first_name="John", last_name="Doe")

        assert user.get_full_name() == "John Doe"

    @pytest.mark.django_db
    def test_get_full_name_without_names_returns_email(self):
        """Проверка: get_full_name() возвращает email если имен нет"""
        user = User.objects.create_user(email="test@example.com", password="pass")

        assert user.get_full_name() == "test@example.com"

    @pytest.mark.django_db
    def test_user_has_optional_fields(self):
        """Проверка: пользователь может иметь avatar, phone, country"""
        user = User.objects.create_user(
            email="test@example.com", password="pass", phone="+79001234567", country="Russia"
        )

        assert user.phone == "+79001234567"
        assert user.country == "Russia"
        assert not user.avatar  # По умолчанию пустой (None или '')

    @pytest.mark.django_db
    def test_user_inherits_from_base_model(self):
        """Проверка: User наследует is_active от BaseModel"""
        user = User.objects.create_user(email="test@example.com", password="pass")

        # is_active по умолчанию True (из BaseModel)
        assert user.is_active is True
        assert hasattr(user, "soft_delete")

    @pytest.mark.django_db
    def test_user_soft_delete(self):
        """Проверка: мягкое удаление пользователя"""
        user = User.objects.create_user(email="test@example.com", password="pass")

        user.soft_delete()

        assert user.is_active is False
        # Пользователь остается в БД
        assert User.objects.filter(id=user.id).exists()

    @pytest.mark.django_db
    def test_user_meta_permissions(self):
        """Проверка: модель имеет кастомное разрешение"""
        permissions = [p[0] for p in User._meta.permissions]
        assert "can_block_user" in permissions

    @pytest.mark.django_db
    def test_username_field_is_email(self):
        """Проверка: USERNAME_FIELD = 'email'"""
        assert User.USERNAME_FIELD == "email"

    @pytest.mark.django_db
    def test_required_fields(self):
        """Проверка: REQUIRED_FIELDS содержит username"""
        assert "username" in User.REQUIRED_FIELDS
