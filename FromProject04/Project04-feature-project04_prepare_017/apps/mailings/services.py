"""
Сервисы для приложения mailings.

Содержит бизнес-логику для управления получателями, сообщениями и рассылками.
"""

from typing import Any, Optional, cast

from apps.core.mixins import LoggingMixin, OwnerFilterMixin
from apps.core.services import BaseCRUDService

from .models import Attempt, Mailing, Message, Recipient


class RecipientService(BaseCRUDService[Recipient], OwnerFilterMixin, LoggingMixin):
    """
    Сервис для управления получателями рассылок.

    Предоставляет CRUD операции с фильтрацией по владельцу и логированием.
    """

    def __init__(self):
        super().__init__(Recipient)

    def create(self, data: dict[str, Any], owner: Optional[Any] = None) -> Optional[Recipient]:
        """Создать получателя."""
        recipient = super().create(data=data, owner=owner)
        if recipient and owner:
            self.log_action("CREATE", recipient, owner)
        return recipient

    def update(self, obj_id: int, data: dict[str, Any], user: Optional[Any] = None) -> Optional[Recipient]:
        """Обновить получателя."""
        recipient = super().update(obj_id=obj_id, data=data, user=user)
        if recipient and user:
            self.log_action("UPDATE", recipient, user)
        return recipient

    def delete(self, obj_id: int, user: Optional[Any] = None, soft: bool = True) -> bool:
        """Удалить получателя (мягкое удаление)."""
        recipient = self.get_by_id(obj_id)
        if recipient and user:
            self.log_action("DELETE", recipient, user)
        return super().delete(obj_id, user=user, soft=soft)


class MessageService(BaseCRUDService[Message], OwnerFilterMixin, LoggingMixin):
    """
    Сервис для управления сообщениями.

    Предоставляет CRUD операции с фильтрацией по владельцу и логированием.
    """

    def __init__(self):
        super().__init__(Message)

    def create(self, data: dict[str, Any], owner: Optional[Any] = None) -> Optional[Message]:
        """Создать сообщение."""
        message = super().create(data=data, owner=owner)
        if message and owner:
            self.log_action("CREATE", message, owner)
        return message

    def update(self, obj_id: int, data: dict[str, Any], user: Optional[Any] = None) -> Optional[Message]:
        """Обновить сообщение."""
        message = super().update(obj_id=obj_id, data=data, user=user)
        if message and user:
            self.log_action("UPDATE", message, user)
        return message

    def delete(self, obj_id: int, user: Optional[Any] = None, soft: bool = True) -> bool:
        """Удалить сообщение (мягкое удаление)."""
        message = self.get_by_id(obj_id)
        if message and user:
            self.log_action("DELETE", message, user)
        return super().delete(obj_id, user=user, soft=soft)


class MailingService(BaseCRUDService[Mailing], OwnerFilterMixin, LoggingMixin):
    """
    Сервис для управления рассылками.

    Предоставляет CRUD операции, специфичную бизнес-логику и логирование.
    """

    def __init__(self):
        super().__init__(Mailing)

    def create(self, data: dict[str, Any], owner: Optional[Any] = None) -> Optional[Mailing]:
        """Создать рассылку."""
        mailing = super().create(data=data, owner=owner)
        if mailing and owner:
            self.log_action("CREATE", mailing, owner)
        return mailing

    def update(self, obj_id: int, data: dict[str, Any], user: Optional[Any] = None) -> Optional[Mailing]:
        """Обновить рассылку."""
        mailing = super().update(obj_id=obj_id, data=data, user=user)
        if mailing and user:
            self.log_action("UPDATE", mailing, user)
        return mailing

    def delete(self, obj_id: int, user: Optional[Any] = None, soft: bool = True) -> bool:
        """Удалить рассылку (мягкое удаление)."""
        mailing = self.get_by_id(obj_id)
        if mailing and user:
            self.log_action("DELETE", mailing, user)
        return super().delete(obj_id, user=user, soft=soft)

    def add_recipients(
        self, mailing_id: int, recipient_ids: list[int], user: Optional[Any] = None
    ) -> Optional[Mailing]:
        """
        Добавляет получателей к рассылке.

        ВАЖНО: Проверяет права пользователя на редактирование рассылки.

        Args:
            mailing_id: ID рассылки
            recipient_ids: Список ID получателей
            user: Пользователь для проверки прав

        Returns:
            Mailing: Обновленная рассылка или None при ошибке
        """
        try:
            mailing = self.model_class.objects.get(id=mailing_id, is_active=True)
        except self.model_class.DoesNotExist:
            self.add_error(f"Рассылка с ID {mailing_id} не найдена")
            return None

        # Проверка прав на редактирование
        if hasattr(mailing, "can_edit") and not mailing.can_edit(user):
            self.add_error("Нет прав на редактирование этой рассылки")
            return None

        mailing.recipients.add(*recipient_ids)
        return cast(Mailing, Mailing.objects.get(id=mailing.id))  # type: ignore[attr-defined]

    def remove_recipients(
        self, mailing_id: int, recipient_ids: list[int], user: Optional[Any] = None
    ) -> Optional[Mailing]:
        """
        Удаляет получателей из рассылки.

        ВАЖНО: Проверяет права пользователя на редактирование рассылки.

        Args:
            mailing_id: ID рассылки
            recipient_ids: Список ID получателей
            user: Пользователь для проверки прав

        Returns:
            Mailing: Обновленная рассылка или None при ошибке
        """
        try:
            mailing = self.model_class.objects.get(id=mailing_id, is_active=True)
        except self.model_class.DoesNotExist:
            self.add_error(f"Рассылка с ID {mailing_id} не найдена")
            return None

        # Проверка прав на редактирование
        if hasattr(mailing, "can_edit") and not mailing.can_edit(user):
            self.add_error("Нет прав на редактирование этой рассылки")
            return None

        mailing.recipients.remove(*recipient_ids)
        return cast(Mailing, Mailing.objects.get(id=mailing.id))  # type: ignore[attr-defined]

    def get_active_mailings(self, user=None):
        """
        Возвращает активные (запущенные) рассылки.

        Args:
            user: Пользователь для фильтрации

        Returns:
            QuerySet: Активные рассылки
        """
        queryset = self.model_class.objects.filter(status=Mailing.STATUS_RUNNING)

        if user:
            queryset = self.filter_by_owner(queryset, user)

        return queryset


class AttemptService(BaseCRUDService[Attempt]):
    """
    Сервис для управления попытками отправки.

    Не использует OwnerFilterMixin, т.к. Attempt не имеет owner.
    """

    def __init__(self):
        super().__init__(Attempt)

    def create(self, data: dict[str, Any], owner: Optional[Any] = None) -> Optional[Attempt]:
        """Создать попытку отправки."""
        return super().create(data=data, owner=owner)

    def get_for_mailing(self, mailing_id: int):
        """
        Возвращает все попытки отправки для рассылки.

        Args:
            mailing_id: ID рассылки

        Returns:
            QuerySet: Попытки отправки
        """
        return self.model_class.objects.filter(mailing_id=mailing_id)

    def get_successful(self, mailing_id: int):
        """
        Возвращает успешные попытки отправки для рассылки.

        Args:
            mailing_id: ID рассылки

        Returns:
            QuerySet: Успешные попытки
        """
        return self.model_class.objects.filter(mailing_id=mailing_id, status=Attempt.STATUS_SUCCESS)

    def get_failed(self, mailing_id: int):
        """
        Возвращает неудачные попытки отправки для рассылки.

        Args:
            mailing_id: ID рассылки

        Returns:
            QuerySet: Неудачные попытки
        """
        return self.model_class.objects.filter(mailing_id=mailing_id, status=Attempt.STATUS_FAILURE)
