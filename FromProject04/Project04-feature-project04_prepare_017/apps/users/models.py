"""
Модели для приложения users.

Содержит кастомную модель пользователя с email-аутентификацией.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import BaseModel

from .managers import UserManager


class User(AbstractUser, BaseModel):
    """
    Кастомная модель пользователя.

    Расширяет стандартную модель Django:
    - Email используется для аутентификации (USERNAME_FIELD)
    - Добавлены поля: avatar, phone, country
    - Наследует BaseModel для is_active и мягкого удаления
    """

    email: models.EmailField = models.EmailField(
        verbose_name="Email адрес", unique=True, help_text="Email для входа в систему"
    )

    avatar: models.ImageField = models.ImageField(
        upload_to="users/avatars/%Y/%m/%d/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text="Фото профиля пользователя",
    )

    phone: models.CharField = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True, help_text="Контактный телефон"
    )

    country: models.CharField = models.CharField(
        max_length=100, verbose_name="Страна", blank=True, null=True, help_text="Страна проживания"
    )

    is_email_verified: models.BooleanField = models.BooleanField(
        default=False, verbose_name="Email подтверждён", help_text="Подтверждён ли email пользователя"
    )

    verification_token: models.CharField = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        verbose_name="Токен подтверждения",
        help_text="Уникальный токен для подтверждения email",
    )

    token_created_at: models.DateTimeField = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата создания токена", help_text="Когда был создан токен подтверждения"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]
        permissions = [
            ("can_block_user", "Может блокировать пользователей"),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def is_manager(self):
        """Проверяет, является ли пользователь менеджером."""
        return self.groups.filter(name="Managers").exists() or self.is_superuser
