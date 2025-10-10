"""
Тесты для management команд приложения mailings.
"""

from datetime import timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.mailings.models import Attempt, Mailing, Message, Recipient


@pytest.fixture
def user(django_user_model):
    """Фикстура: пользователь для тестов"""
    return django_user_model.objects.create_user(email="test@example.com", password="testpass123")


@pytest.fixture
def message(user):
    """Фикстура: сообщение для рассылки"""
    return Message.objects.create(subject="Test Subject", body="Test message body", owner=user)


@pytest.fixture
def recipients(user):
    """Фикстура: список получателей"""
    return [
        Recipient.objects.create(email=f"recipient{i}@example.com", full_name=f"Recipient {i}", owner=user)
        for i in range(3)
    ]


@pytest.fixture
def mailing_created(user, message, recipients):
    """Фикстура: рассылка в статусе Created"""
    mailing = Mailing.objects.create(
        start_datetime=timezone.now() - timedelta(hours=1),
        end_datetime=timezone.now() + timedelta(hours=1),
        status=Mailing.STATUS_CREATED,
        message=message,
        owner=user,
    )
    mailing.recipients.set(recipients)
    return mailing


@pytest.fixture
def mailing_running(user, message, recipients):
    """Фикстура: рассылка в статусе Running"""
    mailing = Mailing.objects.create(
        start_datetime=timezone.now() - timedelta(hours=1),
        end_datetime=timezone.now() + timedelta(hours=1),
        status=Mailing.STATUS_RUNNING,
        message=message,
        owner=user,
    )
    mailing.recipients.set(recipients)
    return mailing


class TestSendMailingCommand:
    """Тесты для команды send_mailing"""

    @pytest.mark.django_db
    @patch("django.core.mail.send_mail")
    def test_sends_emails_to_all_recipients(self, mock_send_mail, mailing_created):
        """Проверка: команда отправляет email всем получателям"""
        mock_send_mail.return_value = 1  # Успешная отправка

        call_command("send_mailing", mailing_created.pk, stdout=StringIO())

        # Проверяем что send_mail вызвана 3 раза (по числу получателей)
        assert mock_send_mail.call_count == 3

    @pytest.mark.django_db
    @patch("django.core.mail.send_mail")
    def test_creates_attempt_records(self, mock_send_mail, mailing_created):
        """Проверка: команда создаёт Attempt записи"""
        mock_send_mail.return_value = 1

        call_command("send_mailing", mailing_created.pk, stdout=StringIO())

        # Проверяем что созданы Attempt записи
        attempts = Attempt.objects.filter(mailing=mailing_created)
        assert attempts.count() == 3  # По числу получателей

    @pytest.mark.django_db
    @patch("django.core.mail.send_mail")
    def test_attempt_status_success_on_successful_send(self, mock_send_mail, mailing_created):
        """Проверка: Attempt.status = Success при успешной отправке"""
        mock_send_mail.return_value = 1

        call_command("send_mailing", mailing_created.pk, stdout=StringIO())

        attempts = Attempt.objects.filter(mailing=mailing_created)
        for attempt in attempts:
            assert attempt.status == Attempt.STATUS_SUCCESS

    @pytest.mark.django_db
    @patch("apps.mailings.management.commands.send_mailing.send_mail")
    def test_attempt_status_failure_on_error(self, mock_send_mail, mailing_created):
        """Проверка: Attempt.status = Failure при ошибке отправки"""
        mock_send_mail.side_effect = Exception("SMTP error")

        call_command("send_mailing", mailing_created.pk, stdout=StringIO())

        attempts = Attempt.objects.filter(mailing=mailing_created)
        for attempt in attempts:
            assert attempt.status == Attempt.STATUS_FAILURE
            assert "SMTP error" in attempt.server_response

    @pytest.mark.django_db
    @patch("apps.mailings.management.commands.send_mailing.send_mail")
    def test_changes_mailing_status_to_running(self, mock_send_mail, mailing_created):
        """Проверка: статус рассылки меняется на Running во время отправки"""

        # Создаём side_effect который проверяет статус во время отправки
        def check_status_during_send(**kwargs):
            mailing_created.refresh_from_db()
            # Во время первого вызова статус должен быть RUNNING
            if mock_send_mail.call_count == 1:
                assert mailing_created.status == Mailing.STATUS_RUNNING
            return 1

        mock_send_mail.side_effect = check_status_during_send

        call_command("send_mailing", mailing_created.pk, stdout=StringIO())

    @pytest.mark.django_db
    @patch("django.core.mail.send_mail")
    def test_changes_mailing_status_to_completed(self, mock_send_mail, mailing_created):
        """Проверка: статус рассылки меняется на Completed после отправки"""
        mock_send_mail.return_value = 1

        call_command("send_mailing", mailing_created.pk, stdout=StringIO())

        mailing_created.refresh_from_db()
        # После отправки всем получателям статус должен быть Completed
        assert mailing_created.status == Mailing.STATUS_COMPLETED

    @pytest.mark.django_db
    def test_only_processes_created_mailings(self, mailing_running):
        """Проверка: команда обрабатывает только рассылки в статусе Created"""
        out = StringIO()
        call_command("send_mailing", mailing_running.pk, stdout=out)

        output = out.getvalue()
        assert "уже обработана" in output.lower() or "не найдена" in output.lower()

    @pytest.mark.django_db
    @patch("django.core.mail.send_mail")
    def test_uses_message_subject_and_body(self, mock_send_mail, mailing_created):
        """Проверка: используется subject и body из Message"""
        mock_send_mail.return_value = 1

        call_command("send_mailing", mailing_created.pk, stdout=StringIO())

        # Проверяем что send_mail вызвана с правильными параметрами
        calls = mock_send_mail.call_args_list
        for call in calls:
            args, kwargs = call
            assert kwargs["subject"] == "Test Subject"
            assert kwargs["message"] == "Test message body"

    @pytest.mark.django_db
    @patch("apps.mailings.management.commands.send_mailing.send_mail")
    def test_sends_to_correct_recipient_emails(self, mock_send_mail, mailing_created):
        """Проверка: email отправляются на правильные адреса получателей"""
        mock_send_mail.return_value = 1

        call_command("send_mailing", mailing_created.pk, stdout=StringIO())

        # Собираем все адреса получателей из вызовов
        sent_to = []
        for call in mock_send_mail.call_args_list:
            args, kwargs = call
            sent_to.extend(kwargs["recipient_list"])

        # Проверяем что email отправлены всем получателям
        expected_emails = {r.email for r in mailing_created.recipients.all()}
        assert set(sent_to) == expected_emails

    @pytest.mark.django_db
    def test_handles_nonexistent_mailing_id(self):
        """Проверка: команда обрабатывает несуществующий ID рассылки"""
        out = StringIO()
        call_command("send_mailing", 99999, stdout=out)

        output = out.getvalue()
        assert "не найдена" in output.lower() or "does not exist" in output.lower()

    @pytest.mark.django_db
    @patch("django.core.mail.send_mail")
    def test_command_output_shows_progress(self, mock_send_mail, mailing_created):
        """Проверка: команда выводит информацию о прогрессе"""
        mock_send_mail.return_value = 1

        out = StringIO()
        call_command("send_mailing", mailing_created.pk, stdout=out)

        output = out.getvalue()
        assert "отправ" in output.lower() or "send" in output.lower()

    @pytest.mark.django_db
    @patch("django.core.mail.send_mail")
    def test_mailing_without_recipients(self, mock_send_mail, user, message):
        """Проверка: обработка рассылки без получателей"""
        mailing = Mailing.objects.create(
            start_datetime=timezone.now() - timedelta(hours=1),
            end_datetime=timezone.now() + timedelta(hours=1),
            status=Mailing.STATUS_CREATED,
            message=message,
            owner=user,
        )
        # Не добавляем получателей

        out = StringIO()
        call_command("send_mailing", mailing.pk, stdout=out)

        # Не должно быть попыток отправки
        assert mock_send_mail.call_count == 0
        mailing.refresh_from_db()
        assert mailing.status == Mailing.STATUS_COMPLETED
