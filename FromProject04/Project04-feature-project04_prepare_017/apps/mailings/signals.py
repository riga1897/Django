"""
Сигналы для инвалидации кеша.

При создании/изменении/удалении рассылок или получателей
автоматически инвалидируется кеш пользователя для статистики.

ВАЖНО: Известные теоретические ограничения Django signals:
- QuerySet.update() и bulk operations НЕ вызывают signals
- В текущем проекте это НЕ проблема, так как:
  * Все CRUD операции используют BaseCRUDService.update() → obj.save()
  * Views используют forms → instance.save()
  * Management commands используют instance.save()
  * QuerySet.update() нигде не используется в коде проекта

Рекомендация для будущих изменений:
- Продолжайте использовать instance.save() через service layer
- Избегайте прямых вызовов QuerySet.update() в новом коде
- При необходимости bulk updates - вручную инвалидируйте кеш
"""

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.mailings.models import Mailing, Recipient


def invalidate_user_cache(user_id):
    """
    Инвалидирует все кеши пользователя для статистики главной страницы.

    Args:
        user_id: ID пользователя
    """
    cache_keys = [
        f"user_{user_id}_total_mailings",
        f"user_{user_id}_active_mailings",
        f"user_{user_id}_unique_recipients",
    ]

    for key in cache_keys:
        cache.delete(key)


@receiver(pre_save, sender=Mailing)
def invalidate_mailing_cache_on_owner_change(sender, instance, **kwargs):
    """
    Инвалидирует кеш при изменении владельца рассылки.

    Если owner_id изменился, инвалидируем кеш ОБОИХ пользователей:
    - Старого владельца (чтобы у него обновилась статистика)
    - Нового владельца (чтобы у него появилась рассылка в статистике)
    """
    if instance.pk:
        try:
            old_instance = Mailing.objects.get(pk=instance.pk)
            if old_instance.owner_id != instance.owner_id:  # type: ignore[attr-defined]
                invalidate_user_cache(old_instance.owner_id)  # type: ignore[attr-defined]
                invalidate_user_cache(instance.owner_id)  # type: ignore[attr-defined]
        except Mailing.DoesNotExist:
            pass


@receiver([post_save, post_delete], sender=Mailing)
def invalidate_mailing_cache(sender, instance, **kwargs):
    """
    Инвалидирует кеш при создании/изменении/удалении рассылки.

    Вызывается автоматически Django при:
    - Создании новой рассылки
    - Изменении существующей рассылки (статус, даты, is_active и т.д.)
    - Удалении рассылки
    """
    invalidate_user_cache(instance.owner_id)  # type: ignore[attr-defined]


@receiver(pre_save, sender=Recipient)
def invalidate_recipient_cache_on_owner_change(sender, instance, **kwargs):
    """
    Инвалидирует кеш при изменении владельца получателя.

    Если owner_id изменился, инвалидируем кеш ОБОИХ пользователей.
    """
    if instance.pk:
        try:
            old_instance = Recipient.objects.get(pk=instance.pk)
            if old_instance.owner_id != instance.owner_id:  # type: ignore[attr-defined]
                invalidate_user_cache(old_instance.owner_id)  # type: ignore[attr-defined]
                invalidate_user_cache(instance.owner_id)  # type: ignore[attr-defined]
        except Recipient.DoesNotExist:
            pass


@receiver([post_save, post_delete], sender=Recipient)
def invalidate_recipient_cache(sender, instance, **kwargs):
    """
    Инвалидирует кеш при создании/изменении/удалении получателя.

    Вызывается автоматически Django при:
    - Создании нового получателя
    - Изменении существующего получателя (email, is_active и т.д.)
    - Удалении получателя
    """
    invalidate_user_cache(instance.owner_id)  # type: ignore[attr-defined]
