"""
Management команда для отправки email-рассылки.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from apps.mailings.models import Attempt, Mailing

logger = logging.getLogger("apps.mailings")


class Command(BaseCommand):
    """
    Отправляет email-рассылку по ID.

    Логика:
    1. Проверяет что рассылка существует и в статусе Created
    2. Меняет статус на Running
    3. Отправляет email всем получателям
    4. Создаёт Attempt записи для каждой попытки
    5. Меняет статус на Completed
    """

    help = "Отправляет email-рассылку по указанному ID"

    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument("mailing_id", type=int, help="ID рассылки для отправки")

    def _get_mailing(self, mailing_id):
        """Получить рассылку по ID или вывести ошибку"""
        try:
            return Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Рассылка с ID {mailing_id} не найдена."))
            return None

    def _send_to_recipient(self, mailing, recipient, verbosity):
        """Отправить email одному получателю и создать Attempt запись"""
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
                trigger_type=Attempt.TRIGGER_COMMAND,
                status=Attempt.STATUS_SUCCESS,
                server_response="Email отправлен успешно",
            )
            if verbosity >= 2:
                self.stdout.write(f"  ✓ Отправлено: {recipient.email}")
            return True
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                run_number=mailing.current_run,
                trigger_type=Attempt.TRIGGER_COMMAND,
                status=Attempt.STATUS_FAILURE,
                server_response=str(e),
            )
            logger.error(f"Ошибка отправки рассылки #{mailing.pk} получателю {recipient.email}: {e}", exc_info=True)
            if verbosity >= 1:
                self.stdout.write(self.style.ERROR(f"  ✗ Ошибка для {recipient.email}: {e}"))
            return False

    def handle(self, *args, **options):
        """Основная логика команды"""
        mailing_id = options["mailing_id"]
        verbosity = options.get("verbosity", 1)

        # Получаем рассылку
        mailing = self._get_mailing(mailing_id)
        if not mailing:
            return

        # Проверяем статус
        if mailing.status != Mailing.STATUS_CREATED:
            self.stdout.write(self.style.WARNING(f"Рассылка #{mailing_id} уже обработана (статус: {mailing.status})."))
            return

        # Получаем получателей
        recipients = mailing.recipients.all()
        if not recipients.exists():
            self.stdout.write(
                self.style.WARNING(f"Рассылка #{mailing_id} не имеет получателей. Устанавливаю статус Completed.")
            )
            mailing.status = Mailing.STATUS_COMPLETED
            mailing.save(update_fields=["status"])
            return

        # Меняем статус на Running
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save(update_fields=["status"])

        logger.info(
            f"Начало отправки рассылки #{mailing_id}: '{mailing.message.subject}' для {recipients.count()} получателей"
        )

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(f"Начинаю отправку рассылки #{mailing_id} для {recipients.count()} получателей...")
            )

        # Отправляем email каждому получателю
        success_count = sum(1 for recipient in recipients if self._send_to_recipient(mailing, recipient, verbosity))
        failure_count = recipients.count() - success_count

        # Меняем статус на Completed
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.save(update_fields=["status"])

        logger.info(f"Рассылка #{mailing_id} завершена. Успешно: {success_count}, Ошибки: {failure_count}")

        # Выводим итоговую статистику
        self.stdout.write(
            self.style.SUCCESS(
                f"\nРассылка #{mailing_id} завершена. Успешно: {success_count}, Ошибки: {failure_count}"
            )
        )
