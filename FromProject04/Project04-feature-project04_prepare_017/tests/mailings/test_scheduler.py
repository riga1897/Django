"""
Тесты для планировщика автоматической отправки рассылок.

TDD подход: RED-GREEN-REFACTOR
Эти тесты написаны ДО реализации scheduler.py
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.mailings.models import Attempt, Mailing, Message, Recipient


@pytest.fixture
def user(django_user_model):
    """Фикстура: пользователь для тестов"""
    return django_user_model.objects.create_user(email="scheduler_test@example.com", password="testpass123")


@pytest.fixture
def message(user):
    """Фикстура: сообщение для рассылки"""
    return Message.objects.create(subject="Scheduled Test Subject", body="Scheduled test message body", owner=user)


@pytest.fixture
def recipients(user):
    """Фикстура: список получателей"""
    return [
        Recipient.objects.create(email=f"scheduled{i}@example.com", full_name=f"Scheduled Recipient {i}", owner=user)
        for i in range(2)
    ]


@pytest.fixture
def mailing_ready_to_send(user, message, recipients):
    """Фикстура: рассылка готова к отправке (Created, в нужном временном диапазоне)"""
    mailing = Mailing.objects.create(
        start_datetime=timezone.now() - timedelta(minutes=10),  # Началась 10 минут назад
        end_datetime=timezone.now() + timedelta(hours=2),  # Закончится через 2 часа
        status=Mailing.STATUS_CREATED,
        message=message,
        owner=user,
    )
    mailing.recipients.set(recipients)
    return mailing


@pytest.fixture
def mailing_not_started(user, message, recipients):
    """Фикстура: рассылка еще не началась (start_datetime в будущем)"""
    mailing = Mailing.objects.create(
        start_datetime=timezone.now() + timedelta(hours=1),  # Начнется через 1 час
        end_datetime=timezone.now() + timedelta(hours=3),
        status=Mailing.STATUS_CREATED,
        message=message,
        owner=user,
    )
    mailing.recipients.set(recipients)
    return mailing


@pytest.fixture
def mailing_already_ended(user, message, recipients):
    """Фикстура: рассылка уже закончилась (end_datetime в прошлом)"""
    mailing = Mailing.objects.create(
        start_datetime=timezone.now() - timedelta(hours=3),
        end_datetime=timezone.now() - timedelta(hours=1),  # Закончилась 1 час назад
        status=Mailing.STATUS_CREATED,
        message=message,
        owner=user,
    )
    mailing.recipients.set(recipients)
    return mailing


@pytest.fixture
def mailing_already_running(user, message, recipients):
    """Фикстура: рассылка уже в статусе Running и успешно отправлена"""
    mailing = Mailing.objects.create(
        start_datetime=timezone.now() - timedelta(minutes=10),
        end_datetime=timezone.now() + timedelta(hours=2),
        status=Mailing.STATUS_RUNNING,
        successfully_sent=True,
        message=message,
        owner=user,
    )
    mailing.recipients.set(recipients)
    return mailing


@pytest.fixture
def mailing_already_completed(user, message, recipients):
    """Фикстура: рассылка уже в статусе Completed"""
    mailing = Mailing.objects.create(
        start_datetime=timezone.now() - timedelta(hours=2),
        end_datetime=timezone.now() + timedelta(hours=1),
        status=Mailing.STATUS_COMPLETED,
        successfully_sent=True,
        message=message,
        owner=user,
    )
    mailing.recipients.set(recipients)
    return mailing


@pytest.mark.django_db
class TestSchedulerCheckAndSend:
    """Тесты для функции check_and_send_mailings()"""

    @patch("apps.mailings.scheduler.send_mail")
    def test_finds_mailings_ready_to_send(self, mock_send_mail, mailing_ready_to_send):
        """
        Проверка: scheduler находит рассылки готовые к отправке
        (Created статус, start_datetime <= now <= end_datetime)
        """
        from apps.mailings.scheduler import check_and_send_mailings

        mock_send_mail.return_value = 1

        check_and_send_mailings()

        # Проверяем что send_mail был вызван (рассылка обработана)
        assert mock_send_mail.call_count == 2  # 2 получателя

    @patch("apps.mailings.scheduler.send_mail")
    def test_ignores_mailings_not_started(self, mock_send_mail, mailing_not_started):
        """
        Проверка: scheduler игнорирует рассылки с start_datetime в будущем
        """
        from apps.mailings.scheduler import check_and_send_mailings

        check_and_send_mailings()

        # send_mail НЕ должен быть вызван
        assert mock_send_mail.call_count == 0

        # Статус должен остаться Created
        mailing_not_started.refresh_from_db()
        assert mailing_not_started.status == Mailing.STATUS_CREATED

    @patch("apps.mailings.scheduler.send_mail")
    def test_ignores_mailings_already_ended(self, mock_send_mail, mailing_already_ended):
        """
        Проверка: scheduler игнорирует рассылки с end_datetime в прошлом
        """
        from apps.mailings.scheduler import check_and_send_mailings

        check_and_send_mailings()

        # send_mail НЕ должен быть вызван
        assert mock_send_mail.call_count == 0

    @patch("apps.mailings.scheduler.send_mail")
    def test_ignores_running_mailings(self, mock_send_mail, mailing_already_running):
        """
        Проверка: scheduler игнорирует рассылки с successfully_sent=True
        """
        from apps.mailings.scheduler import check_and_send_mailings

        check_and_send_mailings()

        # send_mail НЕ должен быть вызван (рассылка уже отправлена)
        assert mock_send_mail.call_count == 0

    @patch("apps.mailings.scheduler.send_mail")
    def test_ignores_completed_mailings(self, mock_send_mail, mailing_already_completed):
        """
        Проверка: scheduler игнорирует рассылки в статусе Completed
        """
        from apps.mailings.scheduler import check_and_send_mailings

        check_and_send_mailings()

        # send_mail НЕ должен быть вызван
        assert mock_send_mail.call_count == 0

    @patch("apps.mailings.scheduler.send_mail")
    def test_changes_status_to_completed(self, mock_send_mail, mailing_ready_to_send):
        """
        Проверка: scheduler ставит successfully_sent=True и переводит в Completed
        """
        from apps.mailings.scheduler import check_and_send_mailings

        mock_send_mail.return_value = 1

        check_and_send_mailings()

        mailing_ready_to_send.refresh_from_db()
        # После успешной отправки должен быть флаг successfully_sent
        assert mailing_ready_to_send.successfully_sent is True
        # Статус должен перейти в COMPLETED
        assert mailing_ready_to_send.status == Mailing.STATUS_COMPLETED

    @patch("apps.mailings.scheduler.send_mail")
    def test_creates_attempt_records(self, mock_send_mail, mailing_ready_to_send):
        """
        Проверка: scheduler создает Attempt записи для каждого получателя
        """
        from apps.mailings.scheduler import check_and_send_mailings

        mock_send_mail.return_value = 1

        check_and_send_mailings()

        # Проверяем количество попыток
        attempts = Attempt.objects.filter(mailing=mailing_ready_to_send)
        assert attempts.count() == 2  # 2 получателя

    @patch("apps.mailings.scheduler.send_mail")
    def test_processes_multiple_mailings(self, mock_send_mail, user, message, recipients):
        """
        Проверка: scheduler обрабатывает несколько рассылок за один запуск
        """
        from apps.mailings.scheduler import check_and_send_mailings

        # Создаем 3 рассылки готовые к отправке
        mailings = []
        for _i in range(3):
            mailing = Mailing.objects.create(
                start_datetime=timezone.now() - timedelta(minutes=10),
                end_datetime=timezone.now() + timedelta(hours=2),
                status=Mailing.STATUS_CREATED,
                message=message,
                owner=user,
            )
            mailing.recipients.set(recipients)
            mailings.append(mailing)

        mock_send_mail.return_value = 1

        check_and_send_mailings()

        # Проверяем что все 3 рассылки обработаны (3 рассылки * 2 получателя)
        assert mock_send_mail.call_count == 6

        # Все рассылки должны быть Completed
        for mailing in mailings:
            mailing.refresh_from_db()
            assert mailing.status == Mailing.STATUS_COMPLETED

    @patch("apps.mailings.scheduler.send_mail")
    def test_handles_send_mail_errors(self, mock_send_mail, mailing_ready_to_send):
        """
        Проверка: scheduler обрабатывает ошибки при отправке писем
        """
        from apps.mailings.scheduler import check_and_send_mailings

        mock_send_mail.side_effect = Exception("SMTP connection error")

        check_and_send_mailings()

        # Проверяем что попытки созданы с статусом Failure
        attempts = Attempt.objects.filter(mailing=mailing_ready_to_send)
        assert attempts.count() == 2

        for attempt in attempts:
            assert attempt.status == Attempt.STATUS_FAILURE
            assert "SMTP connection error" in attempt.server_response

    @patch("apps.mailings.scheduler.send_mail")
    @patch("apps.mailings.scheduler.logger")
    def test_logging_on_successful_send(self, mock_logger, mock_send_mail, mailing_ready_to_send):
        """
        Проверка: scheduler логирует успешную отправку
        """
        from apps.mailings.scheduler import check_and_send_mailings

        mock_send_mail.return_value = 1

        check_and_send_mailings()

        # Проверяем что logger.info был вызван (для логирования отправки)
        assert mock_logger.info.called
        # Проверяем что в одном из вызовов есть информация о рассылке
        call_args_list = [str(call) for call in mock_logger.info.call_args_list]
        assert any("рассылк" in str(call).lower() or "mailing" in str(call).lower() for call in call_args_list)

    @patch("apps.mailings.scheduler.send_mail")
    def test_retry_logic_for_failed_mailings(self, mock_send_mail, user, message, recipients):
        """
        Проверка: scheduler повторяет отправку для неудачных попыток без дублирования
        """
        from apps.mailings.scheduler import check_and_send_mailings

        # Создаем рассылку
        mailing = Mailing.objects.create(
            start_datetime=timezone.now() - timedelta(minutes=10),
            end_datetime=timezone.now() + timedelta(hours=2),
            status=Mailing.STATUS_CREATED,
            message=message,
            owner=user,
        )
        mailing.recipients.set(recipients)

        # Первый запуск: первый получатель fails, второй succeeds
        def side_effect_first_run(*args, **kwargs):
            if kwargs["recipient_list"][0] == recipients[0].email:
                raise Exception("SMTP error for first recipient")
            return 1

        mock_send_mail.side_effect = side_effect_first_run
        check_and_send_mailings()

        # Проверяем что созданы 2 попытки: 1 success, 1 failure
        attempts = Attempt.objects.filter(mailing=mailing)
        assert attempts.count() == 2
        assert attempts.filter(status=Attempt.STATUS_SUCCESS).count() == 1
        assert attempts.filter(status=Attempt.STATUS_FAILURE).count() == 1

        # Рассылка должна быть в статусе Running, successfully_sent=False
        mailing.refresh_from_db()
        assert mailing.status == Mailing.STATUS_RUNNING
        assert mailing.successfully_sent is False

        # Второй запуск: теперь все succeeds
        mock_send_mail.side_effect = None
        mock_send_mail.return_value = 1
        check_and_send_mailings()

        # Проверяем что создана еще одна попытка для первого получателя
        attempts = Attempt.objects.filter(mailing=mailing)
        assert attempts.count() == 3  # 2 из первого запуска + 1 из второго

        # Теперь все получатели имеют успешные попытки
        for recipient in recipients:
            success_attempts = attempts.filter(recipient=recipient, status=Attempt.STATUS_SUCCESS)
            assert success_attempts.exists()

        # Рассылка должна быть successfully_sent=True и status=Completed
        mailing.refresh_from_db()
        assert mailing.successfully_sent is True
        assert mailing.status == Mailing.STATUS_COMPLETED
