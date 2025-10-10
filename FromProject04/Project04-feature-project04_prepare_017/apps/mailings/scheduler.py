"""
Планировщик автоматической отправки рассылок.

Функция check_and_send_mailings() проверяет рассылки, которые еще не были
успешно отправлены, и отправляет их. Также переводит в статус Completed
рассылки, которые успешно отправлены или у которых истек срок.

Интеграция с APScheduler происходит в apps/mailings/apps.py
"""

import logging

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from apps.mailings.models import Attempt, Mailing

logger = logging.getLogger(__name__)


def check_and_send_mailings():
    """
    Проверяет и отправляет рассылки, готовые к отправке.
    Также переводит рассылки в статус Completed по истечению времени.

    Логика:
    1. Находит рассылки, которые еще не отправлены успешно
    2. Отправляет их
    3. При полном успехе ставит successfully_sent=True
    4. Переводит в Completed рассылки с successfully_sent=True ИЛИ end_datetime < now
    """
    now = timezone.now()

    # Сохраняем время запуска планировщика в кеш
    cache.set("scheduler_last_run", now, timeout=None)

    # Шаг 1: Отправка рассылок, которые еще не были отправлены успешно
    _send_pending_mailings(now)

    # Шаг 2: Перевод в Completed рассылок, которые завершились
    _complete_finished_mailings(now)


def _send_pending_mailings(now):
    """
    Отправляет рассылки, которые еще не были успешно отправлены.

    Критерии отбора:
    - successfully_sent = False
    - start_datetime <= now <= end_datetime
    - is_active = True
    - owner.is_active = True (владелец не заблокирован)
    """
    mailings_to_send = (
        Mailing.objects.filter(
            successfully_sent=False,
            start_datetime__lte=now,
            end_datetime__gte=now,
            is_active=True,
            owner__is_active=True,
        )
        .select_related("message", "owner")
        .prefetch_related("recipients")
    )

    if not mailings_to_send.exists():
        logger.debug("Нет рассылок готовых к отправке")
        return

    logger.info(f"Найдено {mailings_to_send.count()} рассылок готовых к отправке")

    for mailing in mailings_to_send:
        try:
            _send_single_mailing(mailing)
        except Exception as e:
            logger.error(f"Критическая ошибка при обработке рассылки #{mailing.pk}: {e}", exc_info=True)


def _complete_finished_mailings(now):
    """
    Переводит в статус Completed рассылки, которые завершились.

    Критерии перевода в Completed:
    - successfully_sent = True ИЛИ end_datetime < now
    - status != Completed (еще не завершены)
    """
    mailings_to_complete = (
        Mailing.objects.filter(is_active=True)
        .exclude(status=Mailing.STATUS_COMPLETED)
        .filter(Q(successfully_sent=True) | Q(end_datetime__lt=now))
    )

    completed_count = 0
    for mailing in mailings_to_complete:
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.save(update_fields=["status"])
        completed_count += 1

        if mailing.successfully_sent:
            logger.info(f"Рассылка #{mailing.pk} переведена в Completed (успешно отправлена)")
        else:
            logger.info(f"Рассылка #{mailing.pk} переведена в Completed (истек срок end_datetime)")

    if completed_count > 0:
        logger.info(f"Завершено рассылок: {completed_count}")


def _send_single_mailing(mailing):
    """
    Отправляет одну рассылку всем её получателям.

    Args:
        mailing: Объект Mailing для отправки
    """
    recipients = mailing.recipients.all()

    if not recipients.exists():
        logger.warning(f"Рассылка #{mailing.pk} не имеет получателей. Пропускаю отправку.")
        return

    # Меняем статус на Running (если еще не Running)
    if mailing.status == Mailing.STATUS_CREATED:
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save(update_fields=["status"])

    logger.info(
        f"Начало отправки рассылки #{mailing.pk}: '{mailing.message.subject}' для {recipients.count()} получателей"
    )

    success_count = 0
    failure_count = 0

    for recipient in recipients:
        # Проверяем есть ли уже успешная попытка для этого получателя
        # в ТЕКУЩЕМ запуске (run_number = current_run)
        existing_success = Attempt.objects.filter(
            mailing=mailing, recipient=recipient, run_number=mailing.current_run, status=Attempt.STATUS_SUCCESS
        ).exists()

        if existing_success:
            # Уже есть успешная попытка в текущем запуске - пропускаем
            success_count += 1
            continue

        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            Attempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                run_number=mailing.current_run,
                trigger_type=Attempt.TRIGGER_SCHEDULED,
                status=Attempt.STATUS_SUCCESS,
                server_response="Email отправлен успешно",
            )
            success_count += 1

        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                run_number=mailing.current_run,
                trigger_type=Attempt.TRIGGER_SCHEDULED,
                status=Attempt.STATUS_FAILURE,
                server_response=str(e),
            )
            failure_count += 1

            logger.error(f"Ошибка отправки рассылки #{mailing.pk} получателю {recipient.email}: {e}", exc_info=True)

    # Если все отправлено успешно - ставим флаг
    if failure_count == 0:
        mailing.successfully_sent = True
        mailing.save(update_fields=["successfully_sent"])
        logger.info(f"Рассылка #{mailing.pk} успешно отправлена всем получателям. Успешно: {success_count}")
    else:
        logger.info(f"Рассылка #{mailing.pk} завершена с ошибками. Успешно: {success_count}, Ошибки: {failure_count}")
