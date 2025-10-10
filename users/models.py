from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="E-Mail")

    phone = models.CharField(max_length=35, verbose_name="Телефон", blank=True, null=True,
                             help_text="Введите номер телефона")
    tg_name = models.CharField(max_length=50, verbose_name="Ник Telegram", blank=True, null=True,
                             help_text="Введите ник Telegram")
    avatar = models.ImageField(upload_to="user/avatars/", verbose_name="Аватар", blank=True, null=True,
                             help_text="Загрузите аватар")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
