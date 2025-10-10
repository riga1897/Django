import logging
from typing import Any, Optional

from django.core.cache import cache
from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class OwnerFilterMixin:
    """
    Миксин для фильтрации объектов по владельцу.

    Обеспечивает разграничение доступа:
    - Обычные пользователи видят только свои объекты
    - Менеджеры (is_staff) видят все объекты

    Использование:
        class MailingService(BaseCRUDService, OwnerFilterMixin):
            def get_user_mailings(self, user):
                qs = Mailing.objects.all()
                return self.filter_by_owner(qs, user)
    """

    def filter_by_owner(self, queryset: QuerySet, user: Any) -> QuerySet:
        """
        Фильтрует QuerySet по владельцу с учетом прав пользователя.

        Args:
            queryset: Исходный QuerySet для фильтрации
            user: Пользователь, для которого фильтруем

        Returns:
            Отфильтрованный QuerySet
        """
        if not user:
            return queryset.none()

        if user.is_staff:
            return queryset

        if hasattr(queryset.model, "owner"):
            return queryset.filter(owner=user)

        return queryset

    def can_access(self, obj: Any, user: Any) -> bool:
        """
        Проверяет, может ли пользователь получить доступ к объекту.

        Args:
            obj: Объект для проверки
            user: Пользователь

        Returns:
            True если доступ разрешен
        """
        if not user:
            return False

        if user.is_staff:
            return True

        if hasattr(obj, "owner"):
            return bool(obj.owner == user)

        return True


class LoggingMixin:
    """
    Миксин для логирования действий с объектами.

    Автоматически логирует:
    - Создание объектов
    - Обновление объектов
    - Удаление объектов
    - Ошибки при операциях

    Использование:
        class ClientService(BaseCRUDService, LoggingMixin):
            def create(self, data, owner):
                client = super().create(data, owner)
                if client:
                    self.log_action('CREATE', client, owner)
                return client
    """

    def log_action(self, action: str, obj: Any, user: Optional[Any] = None, **kwargs) -> None:
        """
        Логирует действие с объектом.

        Args:
            action: Тип действия (CREATE, UPDATE, DELETE, VIEW)
            obj: Объект, с которым произведено действие
            user: Пользователь, выполнивший действие
            **kwargs: Дополнительные данные для логирования
        """
        model_name = obj.__class__.__name__
        obj_id = getattr(obj, "id", "unknown")
        user_info = f"User: {user}" if user else "System"

        extra_info = ""
        if kwargs:
            extra_info = f", Extra: {kwargs}"

        log_message = f"{action} {model_name} [ID: {obj_id}], {user_info}{extra_info}"

        if action in ["CREATE", "UPDATE", "DELETE"]:
            logger.info(log_message)
        else:
            logger.debug(log_message)

    def log_error(self, action: str, error: Exception, user: Optional[Any] = None, **kwargs) -> None:
        """
        Логирует ошибку при выполнении действия.

        Args:
            action: Тип действия, при котором произошла ошибка
            error: Объект исключения
            user: Пользователь
            **kwargs: Дополнительные данные
        """
        user_info = f"User: {user}" if user else "System"
        extra_info = ""
        if kwargs:
            extra_info = f", Extra: {kwargs}"

        log_message = f"ERROR in {action}, {user_info}{extra_info}: {str(error)}"
        logger.error(log_message, exc_info=True)


class CacheMixin:
    """
    Миксин для кеширования результатов запросов.

    Позволяет:
    - Кешировать результаты дорогих операций
    - Инвалидировать кеш при изменении данных
    - Настраивать время жизни кеша

    Использование:
        class StatisticsService(BaseService, CacheMixin):
            def get_total_mailings(self):
                cache_key = 'total_mailings'
                cached = self.get_from_cache(cache_key)
                if cached is not None:
                    return cached

                total = Mailing.objects.count()
                self.set_cache(cache_key, total, timeout=300)
                return total
    """

    def get_cache_key(self, *args, **kwargs) -> str:
        """
        Генерирует ключ для кеширования.

        Args:
            *args: Позиционные аргументы для формирования ключа
            **kwargs: Именованные аргументы

        Returns:
            Строка-ключ для кеша
        """
        parts = [str(arg) for arg in args]
        parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return ":".join(parts)

    def get_from_cache(self, cache_key: str) -> Optional[Any]:
        """
        Получает значение из кеша.

        Args:
            cache_key: Ключ кеша

        Returns:
            Значение из кеша или None
        """
        value = cache.get(cache_key)
        if value is not None:
            logger.debug(f"Cache HIT: {cache_key}")
        else:
            logger.debug(f"Cache MISS: {cache_key}")
        return value

    def set_cache(self, cache_key: str, value: Any, timeout: int = 300) -> None:
        """
        Сохраняет значение в кеш.

        Args:
            cache_key: Ключ кеша
            value: Значение для сохранения
            timeout: Время жизни в секундах (по умолчанию 5 минут)
        """
        cache.set(cache_key, value, timeout)
        logger.debug(f"Cache SET: {cache_key}, timeout: {timeout}s")

    def invalidate_cache(self, cache_key: str) -> None:
        """
        Инвалидирует (удаляет) значение из кеша.

        Args:
            cache_key: Ключ кеша для удаления
        """
        cache.delete(cache_key)
        logger.debug(f"Cache INVALIDATE: {cache_key}")

    def invalidate_cache_pattern(self, pattern: str) -> None:
        """
        Инвалидирует все ключи, соответствующие паттерну.

        Args:
            pattern: Паттерн для поиска ключей (например, 'mailing:*')
        """
        try:
            cache.delete_pattern(pattern)  # type: ignore[attr-defined]
            logger.debug(f"Cache INVALIDATE pattern: {pattern}")
        except AttributeError:
            logger.warning("Cache backend does not support pattern deletion")
