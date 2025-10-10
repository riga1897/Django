from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    
    Расширяет стандартную модель Django:
    - Email используется для аутентификации (USERNAME_FIELD)
    - Добавлены поля: avatar, phone, country
    """
    
    email = models.EmailField(
        verbose_name="Email адрес",
        unique=True,
        help_text="Email для входа в систему"
    )
    
    avatar = models.ImageField(
        upload_to="users/avatars/%Y/%m/%d/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text="Фото профиля пользователя"
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        blank=True,
        null=True,
        help_text="Контактный телефон"
    )
    
    country = models.CharField(
        max_length=100,
        verbose_name="Страна",
        blank=True,
        null=True,
        help_text="Страна проживания"
    )
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
