"""
Конфигурация приложения mailings.
"""

import logging
import os
import sys

from django.apps import AppConfig
from django.utils import timezone

logger = logging.getLogger(__name__)

# Глобальный флаг для предотвращения множественного запуска scheduler
_scheduler_started = False


class MailingsConfig(AppConfig):
    """Конфигурация приложения для управления рассылками."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mailings"
    verbose_name = "Управление рассылками"

    def ready(self):
        """
        Регистрация сигналов и запуск планировщика при запуске приложения.
        """
        # Импортируем сигналы для их регистрации
        import apps.mailings.signals  # noqa: F401

        # Запускаем планировщик только в основном процессе Django
        global _scheduler_started

        # В режиме тестирования - не запускаем
        is_testing = "test" in sys.argv or os.environ.get("PYTEST_RUNNING")
        if is_testing:
            return

        # Если scheduler уже запущен в этом процессе - не запускаем повторно
        if _scheduler_started:
            logger.debug("Scheduler уже запущен в этом процессе")
            return

        # В Django runserver с autoreload (по умолчанию):
        # - Родительский процесс (watcher): RUN_MAIN не установлен
        # - Reload процесс (actual server): RUN_MAIN='true'
        #
        # В runserver --noreload: RUN_MAIN не установлен (и только один процесс)
        # В production (gunicorn/uwsgi): RUN_MAIN не установлен
        run_main = os.environ.get("RUN_MAIN")

        # Запускаем scheduler ТОЛЬКО в long-lived server процессах:
        # 1. Django runserver reload процесс (RUN_MAIN='true')
        # 2. Django runserver --noreload
        # 3. Production WSGI servers (gunicorn, uwsgi, daphne)
        #
        # НЕ запускаем в:
        # - Management командах (migrate, collectstatic, createsuperuser)
        # - Родительском процессе runserver (watcher)
        # - Тестовом окружении

        # Позитивная идентификация long-lived server контекстов
        is_long_lived_server = False

        if run_main == "true":
            # Django runserver reload процесс
            is_long_lived_server = True
        else:
            # Проверяем другие серверные контексты
            is_runserver = "runserver" in sys.argv
            is_noreload = "--noreload" in sys.argv

            if is_runserver and is_noreload:
                # Django runserver --noreload
                is_long_lived_server = True
            elif not is_runserver:
                # Проверяем WSGI сервера (gunicorn, uwsgi, daphne)
                # Эти сервера импортируют Django как WSGI app, а не через manage.py
                main_module = sys.argv[0] if sys.argv else ""

                # Проверяем по имени главного модуля
                wsgi_indicators = ["gunicorn", "uwsgi", "daphne", "waitress"]
                has_wsgi_indicator = any(indicator in main_module.lower() for indicator in wsgi_indicators)
                has_server_env = os.environ.get("SERVER_SOFTWARE") or os.environ.get("WSGI_APPLICATION")
                if has_wsgi_indicator or has_server_env:
                    is_long_lived_server = True

        if is_long_lived_server:
            success = self._start_scheduler()
            if success:
                _scheduler_started = True
            else:
                # Scheduler не запустился (обычно из-за недоступности DB)
                # В production это означает что приложение не работает корректно
                # и требует внимания администратора
                logger.error(
                    "Scheduler не запустился. Проверьте доступность БД и "
                    "выполнение миграций. Требуется перезапуск приложения."
                )
        else:
            logger.debug(
                f"Пропуск запуска scheduler: не long-lived server процесс (RUN_MAIN={run_main}, argv={sys.argv[:2]})"
            )

    def _start_scheduler(self):
        """
        Запуск APScheduler для автоматической отправки рассылок.

        Использует MemoryJobStore (задачи хранятся в RAM) вместо DjangoJobStore:
        - Избегает раннего обращения к БД при старте приложения
        - Не создаёт лишних соединений к БД (нет логов переподключений)
        - Быстрее, так как нет сетевых запросов
        - Задача статична и пересоздаётся при каждом запуске сервера

        Создаёт интервальное задание с отложенным первым запуском:
        - Первый запуск настраивается через SCHEDULER_FIRST_RUN_DELAY (по умолчанию: 30 сек)
          (гарантирует полную инициализацию Django и БД)
        - Последующие запуски настраиваются через SCHEDULER_CHECK_INTERVAL_MINUTES

        Переменные окружения (.env):
        - SCHEDULER_FIRST_RUN_DELAY: задержка первого запуска в секундах (по умолчанию: 30)
        - SCHEDULER_CHECK_INTERVAL_MINUTES: интервал проверки в минутах (по умолчанию: 5)

        Returns:
            bool: True если scheduler успешно запущен, False при ошибке
        """
        from apscheduler.schedulers.background import BackgroundScheduler

        from apps.mailings.scheduler import check_and_send_mailings

        try:
            # Читаем настройки из .env
            first_run_delay = int(os.environ.get("SCHEDULER_FIRST_RUN_DELAY", 30))
            check_interval = int(os.environ.get("SCHEDULER_CHECK_INTERVAL_MINUTES", 5))

            # Используем MemoryJobStore (по умолчанию) - задачи хранятся в RAM
            # Не требует обращений к БД, избегает логов переподключений
            scheduler = BackgroundScheduler()

            # Регулярная задача с отложенным первым запуском
            # Первый запуск через N секунд (гарантия инициализации Django/БД)
            # Затем APScheduler автоматически повторяет каждые M минут
            first_run_time = timezone.now() + timezone.timedelta(seconds=first_run_delay)  # type: ignore[attr-defined]

            scheduler.add_job(
                check_and_send_mailings,
                trigger="interval",
                minutes=check_interval,
                id="check_and_send_mailings",
                max_instances=1,  # Только один экземпляр задачи одновременно
                replace_existing=True,  # Заменять существующую задачу при перезапуске
                next_run_time=first_run_time,  # Первый запуск через N сек
            )

            scheduler.start()
            logger.info(
                f"APScheduler запущен (MemoryJobStore): "
                f"первая проверка через {first_run_delay} сек, затем каждые {check_interval} мин"
            )
            return True

        except Exception as e:
            logger.error(f"Ошибка при запуске APScheduler: {e}", exc_info=True)
            return False
