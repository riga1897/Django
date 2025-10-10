from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """
    Абстрактная базовая модель для всех моделей проекта.

    Обеспечивает:
    - Автоматическое отслеживание времени создания и обновления
    - Флаг активности для "мягкого удаления"
    - Единый интерфейс для всех моделей
    """

    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания", help_text="Автоматически устанавливается при создании"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления", help_text="Автоматически обновляется при каждом сохранении"
    )
    is_active: models.BooleanField = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Флаг для мягкого удаления - неактивные объекты можно не показывать",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def soft_delete(self):
        """Мягкое удаление - помечает объект как неактивный"""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def restore(self):
        """Восстановление мягко удаленного объекта"""
        self.is_active = True
        self.save(update_fields=["is_active"])


class OwnedModel(BaseModel):
    """
    Абстрактная модель для объектов с владельцем.

    Используется для:
    - Разграничения доступа (каждый пользователь видит только свои объекты)
    - Автоматического определения владельца
    - Реализации прав доступа (Пользователь vs Менеджер)
    """

    owner: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="%(class)s_owned",
        help_text="Пользователь, создавший этот объект",
    )

    class Meta:
        abstract = True

    def is_owner(self, user):
        """Проверка, является ли пользователь владельцем"""
        return self.owner == user

    def can_edit(self, user):
        """
        Может ли пользователь редактировать объект.

        Согласно ТЗ: только владелец может редактировать.
        Менеджеры НЕ могут редактировать чужие объекты.
        """
        return self.is_owner(user)

    def can_delete(self, user):
        """
        Может ли пользователь удалить объект.

        Согласно ТЗ: только владелец может удалять.
        Менеджеры НЕ могут удалять чужие объекты.
        """
        return self.is_owner(user)
