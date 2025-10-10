import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True, encoding="utf8")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv("DEBUG") == "True")

ALLOWED_HOSTS = ["*"]

# CSRF trusted origins для Replit
CSRF_TRUSTED_ORIGINS = [
    "https://*.repl.co",
    "https://*.repl.dev",
    "https://*.replit.dev",
    "https://*.replit.app",
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Приложения проекта
    "apps.core",
    "apps.users",
    "apps.mailings",
    # Планировщик задач
    "django_apscheduler",
]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.CheckUserActiveMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
        # Persistent connections: держит соединение открытым 10 минут
        # Избегает постоянного открытия/закрытия соединений (логи переподключений)
        # 600 сек > SCHEDULER_CHECK_INTERVAL (по умолчанию 5 мин)
        "CONN_MAX_AGE": 600,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True
USE_THOUSAND_SEPARATOR = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static files caching (browser cache)
# ManifestStaticFilesStorage добавляет хеш к именам файлов для версионирования
# Это позволяет браузеру кешировать статические файлы на длительный срок
# ВАЖНО: Не используем UpdateCacheMiddleware/FetchFromCacheMiddleware для всего сайта!
# Per-site caching опасен для приложений с персональными данными (утечка между пользователями)
if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Authentication settings
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Cache settings
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "mailing-service-cache",
        "TIMEOUT": 300,  # 5 minutes default
    }
}

# Email settings (консоль для разработки, SMTP для production)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "True") == "True"
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "5242880"))  # 5MB default
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# Создаем папку для логов, если её нет (с поддержкой вложенных путей)
LOG_PATH = BASE_DIR / LOG_DIR
LOG_PATH.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "()": "django.utils.log.ServerFormatter",
            "format": "{levelname} {asctime} [{module}] {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": LOG_LEVEL,
        },
    },
    "loggers": {
        "apps": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# Добавляем file handlers только если LOG_TO_FILE=True
if LOG_TO_FILE:
    LOGGING["handlers"]["file"] = {  # type: ignore[index]
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOG_PATH / "django.log",
        "maxBytes": LOG_MAX_SIZE,
        "backupCount": LOG_BACKUP_COUNT,
        "formatter": "verbose",
        "level": LOG_LEVEL,
        "encoding": "utf-8",
    }
    LOGGING["handlers"]["error_file"] = {  # type: ignore[index]
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOG_PATH / "errors.log",
        "maxBytes": LOG_MAX_SIZE,
        "backupCount": LOG_BACKUP_COUNT,
        "formatter": "verbose",
        "level": "ERROR",
        "encoding": "utf-8",
    }
    # Добавляем file handlers к apps logger
    LOGGING["loggers"]["apps"]["handlers"] = ["console", "file", "error_file"]  # type: ignore[index]
    LOGGING["loggers"]["django.request"]["handlers"] = ["console", "error_file"]  # type: ignore[index]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
