import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from django.db import models
from django.db.models import QuerySet

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=models.Model)


class BaseService(ABC):
    """
    Чистая абстракция базового сервиса - контракт для всех сервисов.

    ВАЖНО: Этот класс НЕ содержит никакой реализации!
    Только определяет контракт, который должны выполнять все сервисы.

    Философия:
    - Сервисы инкапсулируют бизнес-логику
    - Контроллеры (views) только вызывают методы сервисов
    - Модели отвечают только за данные
    """

    @abstractmethod
    def validate(self, data: dict[str, Any]) -> bool:
        """
        Валидация данных перед обработкой.

        Args:
            data: Словарь с данными для валидации

        Returns:
            True если данные валидны, False если есть ошибки
        """
        pass  # pragma: no cover


class BaseServiceWithErrors(BaseService):
    """
    Базовая реализация сервиса с поддержкой обработки ошибок.

    Этот класс предоставляет реализацию для работы с ошибками,
    которая используется большинством сервисов в проекте.
    """

    def __init__(self):
        """Инициализация сервиса с пустым списком ошибок"""
        self.errors: list[str] = []

    def add_error(self, error: str) -> None:
        """
        Добавить ошибку в список.

        Args:
            error: Текст ошибки
        """
        self.errors.append(error)
        logger.warning(f"Service error: {error}")

    def has_errors(self) -> bool:
        """
        Проверить наличие ошибок.

        Returns:
            True если есть ошибки, False если нет
        """
        return len(self.errors) > 0

    def clear_errors(self) -> None:
        """Очистить список ошибок"""
        self.errors = []

    def get_errors(self) -> list[str]:
        """
        Получить копию списка ошибок.

        Returns:
            Список сообщений об ошибках
        """
        return self.errors.copy()


class BaseCRUDService(BaseServiceWithErrors, Generic[T]):
    """
    Базовый сервис для CRUD операций с Generic типизацией.

    Предоставляет стандартные операции:
    - Create (создание)
    - Read (чтение)
    - Update (обновление)
    - Delete (удаление)

    Использование:
        class RecipientService(BaseCRUDService[Recipient]):
            def __init__(self):
                super().__init__(Recipient)
    """

    def __init__(self, model_class: type[T]):
        """
        Инициализация CRUD сервиса.

        Args:
            model_class: Класс модели Django для работы
        """
        super().__init__()
        self.model_class = model_class

    def validate(self, data: dict[str, Any]) -> bool:
        """
        Базовая валидация - проверка что данные не пустые.

        Args:
            data: Данные для валидации

        Returns:
            True если валидация пройдена, False если есть ошибки
        """
        if not data:
            self.add_error("Данные не могут быть пустыми")
            return False
        return True

    def get_all(self, user: Optional[Any] = None) -> QuerySet:
        """
        Получить все активные объекты (с учетом прав доступа).

        Логика фильтрации:
        - Обычные пользователи видят только свои объекты
        - Менеджеры (staff) видят все объекты

        Args:
            user: Пользователь для фильтрации

        Returns:
            QuerySet с объектами
        """
        queryset = self.model_class.objects.filter(is_active=True)

        if user and hasattr(self.model_class, "owner") and not user.is_staff:
            queryset = queryset.filter(owner=user)

        return queryset

    def get_by_id(self, obj_id: int, user: Optional[Any] = None) -> Optional[T]:
        """
        Получить объект по ID с проверкой прав доступа.

        Args:
            obj_id: ID объекта
            user: Пользователь для проверки прав доступа

        Returns:
            Объект модели или None если не найден
        """
        try:
            queryset = self.get_all(user)
            return queryset.get(id=obj_id)  # type: ignore[return-value,no-any-return]
        except self.model_class.DoesNotExist:
            self.add_error(f"Объект с ID {obj_id} не найден")
            return None

    def create(self, data: dict[str, Any], owner: Optional[Any] = None) -> Optional[T]:
        """
        Создать новый объект.

        Args:
            data: Данные для создания объекта
            owner: Владелец объекта (для моделей с OwnedModel)

        Returns:
            Созданный объект или None при ошибке
        """
        if not self.validate(data):
            return None

        try:
            if owner and hasattr(self.model_class, "owner"):
                data["owner"] = owner

            obj = self.model_class.objects.create(**data)
            logger.info(f"Created {self.model_class.__name__} with ID {obj.id}")  # type: ignore[attr-defined]
            return obj  # type: ignore[return-value]

        except Exception as e:
            self.add_error(f"Ошибка при создании: {str(e)}")
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            return None

    def update(self, obj_id: int, data: dict[str, Any], user: Optional[Any] = None) -> Optional[T]:
        """
        Обновить существующий объект.

        ВАЖНО: Менеджеры НЕ могут редактировать чужие объекты!
        Проверка прав выполняется через метод can_edit() модели.

        Args:
            obj_id: ID объекта
            data: Данные для обновления
            user: Пользователь для проверки прав

        Returns:
            Обновленный объект или None при ошибке
        """
        # Получаем объект (менеджеры видят все, но НЕ могут редактировать чужие)
        try:
            obj = self.model_class.objects.get(id=obj_id, is_active=True)
        except self.model_class.DoesNotExist:
            self.add_error(f"Объект с ID {obj_id} не найден")
            return None

        # ВАЖНО: Проверка прав на редактирование
        if hasattr(obj, "can_edit") and not obj.can_edit(user):
            self.add_error("Нет прав на редактирование этого объекта")
            logger.warning(f"User {user} attempted to edit {self.model_class.__name__} ID {obj_id} without permission")
            return None

        if not self.validate(data):
            return None

        try:
            for field, value in data.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)

            obj.save()
            logger.info(f"Updated {self.model_class.__name__} with ID {obj.id}")  # type: ignore[attr-defined]
            return obj  # type: ignore[return-value]

        except Exception as e:
            self.add_error(f"Ошибка при обновлении: {str(e)}")
            logger.error(f"Error updating {self.model_class.__name__}: {str(e)}")
            return None

    def delete(self, obj_id: int, user: Optional[Any] = None, soft: bool = True) -> bool:
        """
        Удалить объект.

        ВАЖНО: Менеджеры НЕ могут удалять чужие объекты!
        Проверка прав выполняется через метод can_delete() модели.

        Args:
            obj_id: ID объекта
            user: Пользователь для проверки прав
            soft: True для мягкого удаления (is_active=False), False для полного

        Returns:
            True если удаление успешно, False при ошибке
        """
        # Получаем объект (менеджеры видят все, но НЕ могут удалять чужие)
        try:
            obj = self.model_class.objects.get(id=obj_id, is_active=True)
        except self.model_class.DoesNotExist:
            self.add_error(f"Объект с ID {obj_id} не найден")
            return False

        # ВАЖНО: Проверка прав на удаление
        if hasattr(obj, "can_delete") and not obj.can_delete(user):
            self.add_error("Нет прав на удаление этого объекта")
            logger.warning(
                f"User {user} attempted to delete {self.model_class.__name__} ID {obj_id} without permission"
            )
            return False

        try:
            if soft and hasattr(obj, "soft_delete"):
                obj.soft_delete()
                logger.info(f"Soft deleted {self.model_class.__name__} with ID {obj.id}")  # type: ignore[attr-defined]
            else:
                obj.delete()
                logger.info(f"Hard deleted {self.model_class.__name__} with ID {obj.id}")  # type: ignore[attr-defined]

            return True

        except Exception as e:
            self.add_error(f"Ошибка при удалении: {str(e)}")
            logger.error(f"Error deleting {self.model_class.__name__}: {str(e)}")
            return False

    def count(self, user: Optional[Any] = None) -> int:
        """
        Подсчитать количество объектов с учетом прав доступа.

        Args:
            user: Пользователь для фильтрации

        Returns:
            Количество доступных объектов
        """
        return int(self.get_all(user).count())
