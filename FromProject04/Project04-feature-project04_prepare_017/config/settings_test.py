"""
Настройки Django для тестов.

Импортирует все из settings.py и переопределяет БД на SQLite для быстрых тестов.
"""

from .settings import *  # noqa: F401, F403

# Добавляем тестовое приложение для тестовых моделей
INSTALLED_APPS = list(INSTALLED_APPS)  # noqa: F405
INSTALLED_APPS.append("tests.core")

# Переопределяем БД на SQLite для тестов
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Отключаем миграции для быстрого создания БД в тестах
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Ускоряем тесты с паролями
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Используем локальный email backend для тестов (не отправляем реальные письма)
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
