from typing import Any, ClassVar

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):  # type: ignore[type-arg]
    """Кастомный менеджер для модели User с email в качестве логина."""

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> "User":
        """Создать и сохранить обычного пользователя."""
        if not email:
            raise ValueError("Email обязателен для заполнения")

        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # type: ignore[attr-defined]
        user.save(using=self._db)
        return user  # type: ignore[return-value]

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> "User":
        """Создать и сохранить суперпользователя."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser должен иметь is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Расширяет стандартную модель Django:
    - Email используется для аутентификации (USERNAME_FIELD)
    - Добавлены поля: avatar, phone, country
    """

    username = models.CharField(  # type: ignore[assignment]
        max_length=150, unique=False, blank=True, null=True, verbose_name="Имя пользователя"
    )

    email = models.EmailField(verbose_name="Email адрес", unique=True, help_text="Email для входа в систему")

    avatar = models.ImageField(
        upload_to="users/avatars/%Y/%m/%d/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text="Фото профиля пользователя",
    )

    phone = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True, help_text="Контактный телефон"
    )

    country = models.CharField(
        max_length=100, verbose_name="Страна", blank=True, null=True, help_text="Страна проживания"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    class Meta:  # type: ignore[misc]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return str(self.email)

    def get_full_name(self) -> str:
        """Возвращает полное имя пользователя."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else str(self.email)
