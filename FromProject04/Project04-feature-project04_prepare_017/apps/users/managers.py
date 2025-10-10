"""
Кастомные менеджеры для модели User.
"""

from typing import TYPE_CHECKING, Any, Optional

from django.contrib.auth.models import UserManager as DjangoUserManager

if TYPE_CHECKING:
    from apps.users.models import User


class UserManager(DjangoUserManager):
    """
    Кастомный менеджер для модели User с email-аутентификацией.
    """

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> "User":  # type: ignore[override]
        """
        Создает обычного пользователя.

        Args:
            email: Email пользователя (используется для входа)
            password: Пароль
            **extra_fields: Дополнительные поля

        Returns:
            User: Созданный пользователь
        """
        if not email:
            raise ValueError("Email обязателен для создания пользователя")

        email = self.normalize_email(email)
        # Если username не передан, используем полный email для уникальности
        if "username" not in extra_fields:
            extra_fields["username"] = email

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user  # type: ignore[no-any-return]

    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> "User":  # type: ignore[override]
        """
        Создает суперпользователя.

        Args:
            email: Email пользователя
            password: Пароль
            **extra_fields: Дополнительные поля

        Returns:
            User: Созданный суперпользователь
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)
