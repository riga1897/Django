"""
Тесты для сервисов приложения mailings.

Проверяем:
- RecipientService
- MessageService
- MailingService
- AttemptService
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.mailings.models import Attempt, Mailing, Message, Recipient
from apps.mailings.services import AttemptService, MailingService, MessageService, RecipientService

User = get_user_model()


@pytest.fixture
def user(db):
    """Фикстура для создания пользователя"""
    return User.objects.create_user(email="owner@example.com", password="testpass123", username="owner")


@pytest.fixture
def another_user(db):
    """Фикстура для создания другого пользователя"""
    return User.objects.create_user(email="another@example.com", password="testpass123", username="another")


class TestRecipientService:
    """Тесты для RecipientService"""

    @pytest.mark.django_db
    def test_create_recipient(self, user):
        """Проверка: создание получателя через сервис"""
        service = RecipientService()

        recipient = service.create(
            data={"email": "test@example.com", "full_name": "Test User", "comment": "Test comment"}, owner=user
        )

        assert recipient.email == "test@example.com"
        assert recipient.full_name == "Test User"
        assert recipient.owner == user

    @pytest.mark.django_db
    def test_get_by_id(self, user):
        """Проверка: получение получателя по ID"""
        service = RecipientService()

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test", owner=user)

        found = service.get_by_id(recipient.id)
        assert found == recipient

    @pytest.mark.django_db
    def test_get_all_filters_by_owner(self, user, another_user):
        """Проверка: get_all возвращает только записи владельца"""
        service = RecipientService()

        # Создаем получателей для разных пользователей
        r1 = Recipient.objects.create(email="user1@example.com", full_name="User 1", owner=user)

        r2 = Recipient.objects.create(email="user2@example.com", full_name="User 2", owner=another_user)

        # Получаем только получателей первого пользователя
        recipients = service.get_all(user=user)

        assert r1 in recipients
        assert r2 not in recipients
        assert recipients.count() == 1

    @pytest.mark.django_db
    def test_update_recipient(self, user):
        """Проверка: обновление получателя"""
        service = RecipientService()

        recipient = Recipient.objects.create(email="old@example.com", full_name="Old Name", owner=user)

        updated = service.update(recipient.id, data={"email": "new@example.com", "full_name": "New Name"}, user=user)

        assert updated.email == "new@example.com"
        assert updated.full_name == "New Name"

    @pytest.mark.django_db
    def test_delete_recipient(self, user):
        """Проверка: удаление получателя (soft delete)"""
        service = RecipientService()

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test", owner=user)

        result = service.delete(recipient.id, user=user)

        assert result is True
        recipient.refresh_from_db()
        assert recipient.is_active is False

    @pytest.mark.django_db
    def test_get_active_only(self, user):
        """Проверка: get_all возвращает только активные записи"""
        service = RecipientService()

        active = Recipient.objects.create(email="active@example.com", full_name="Active", owner=user, is_active=True)

        inactive = Recipient.objects.create(
            email="inactive@example.com", full_name="Inactive", owner=user, is_active=False
        )

        recipients = service.get_all(user=user)

        assert active in recipients
        assert inactive not in recipients


class TestMessageService:
    """Тесты для MessageService"""

    @pytest.mark.django_db
    def test_create_message(self, user):
        """Проверка: создание сообщения через сервис"""
        service = MessageService()

        message = service.create(data={"subject": "Test Subject", "body": "Test body content"}, owner=user)

        assert message.subject == "Test Subject"
        assert message.body == "Test body content"
        assert message.owner == user

    @pytest.mark.django_db
    def test_get_by_id(self, user):
        """Проверка: получение сообщения по ID"""
        service = MessageService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        found = service.get_by_id(message.id)
        assert found == message

    @pytest.mark.django_db
    def test_get_all_filters_by_owner(self, user, another_user):
        """Проверка: get_all возвращает только сообщения владельца"""
        service = MessageService()

        m1 = Message.objects.create(subject="Message 1", body="Body 1", owner=user)

        m2 = Message.objects.create(subject="Message 2", body="Body 2", owner=another_user)

        messages = service.get_all(user=user)

        assert m1 in messages
        assert m2 not in messages

    @pytest.mark.django_db
    def test_update_message(self, user):
        """Проверка: обновление сообщения"""
        service = MessageService()

        message = Message.objects.create(subject="Old Subject", body="Old Body", owner=user)

        updated = service.update(message.id, data={"subject": "New Subject", "body": "New Body"}, user=user)

        assert updated.subject == "New Subject"
        assert updated.body == "New Body"

    @pytest.mark.django_db
    def test_delete_message(self, user):
        """Проверка: удаление сообщения (soft delete)"""
        service = MessageService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        result = service.delete(message.id, user=user)

        assert result is True
        message.refresh_from_db()
        assert message.is_active is False


class TestMailingService:
    """Тесты для MailingService"""

    @pytest.mark.django_db
    def test_create_mailing(self, user):
        """Проверка: создание рассылки через сервис"""
        service = MailingService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        mailing = service.create(
            data={
                "start_datetime": timezone.now(),
                "end_datetime": timezone.now() + timedelta(days=1),
                "message": message,
            },
            owner=user,
        )

        assert mailing.message == message
        assert mailing.status == Mailing.STATUS_CREATED
        assert mailing.owner == user

    @pytest.mark.django_db
    def test_get_all_filters_by_owner(self, user, another_user):
        """Проверка: get_all возвращает только рассылки владельца"""
        service = MailingService()

        message1 = Message.objects.create(subject="Test 1", body="Body", owner=user)

        message2 = Message.objects.create(subject="Test 2", body="Body", owner=another_user)

        m1 = Mailing.objects.create(
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(days=1),
            message=message1,
            owner=user,
        )

        m2 = Mailing.objects.create(
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(days=1),
            message=message2,
            owner=another_user,
        )

        mailings = service.get_all(user=user)

        assert m1 in mailings
        assert m2 not in mailings

    @pytest.mark.django_db
    def test_update_mailing(self, user):
        """Проверка: обновление рассылки"""
        service = MailingService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(days=1),
            message=message,
            owner=user,
            status=Mailing.STATUS_CREATED,
        )

        updated = service.update(mailing.id, data={"status": Mailing.STATUS_RUNNING}, user=user)

        assert updated.status == Mailing.STATUS_RUNNING

    @pytest.mark.django_db
    def test_add_recipients_to_mailing(self, user):
        """Проверка: добавление получателей к рассылке"""
        service = MailingService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        recipient1 = Recipient.objects.create(email="r1@example.com", full_name="R1", owner=user)

        recipient2 = Recipient.objects.create(email="r2@example.com", full_name="R2", owner=user)

        result = service.add_recipients(mailing.id, [recipient1.id, recipient2.id], user=user)

        assert result is not None
        mailing.refresh_from_db()
        assert mailing.recipients.count() == 2
        assert recipient1 in mailing.recipients.all()
        assert recipient2 in mailing.recipients.all()

    @pytest.mark.django_db
    def test_remove_recipients_from_mailing(self, user):
        """Проверка: удаление получателей из рассылки"""
        service = MailingService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        recipient1 = Recipient.objects.create(email="r1@example.com", full_name="R1", owner=user)

        recipient2 = Recipient.objects.create(email="r2@example.com", full_name="R2", owner=user)

        mailing.recipients.add(recipient1, recipient2)
        assert mailing.recipients.count() == 2

        result = service.remove_recipients(mailing.id, [recipient1.id], user=user)

        assert result is not None
        mailing.refresh_from_db()
        assert mailing.recipients.count() == 1
        assert recipient1 not in mailing.recipients.all()
        assert recipient2 in mailing.recipients.all()

    @pytest.mark.django_db
    def test_add_recipients_unauthorized(self, user, another_user):
        """Проверка: другой пользователь не может добавлять получателей в чужую рассылку"""
        service = MailingService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        recipient = Recipient.objects.create(email="r1@example.com", full_name="R1", owner=another_user)

        # Попытка другого пользователя добавить получателей
        result = service.add_recipients(mailing.id, [recipient.id], user=another_user)

        assert result is None
        assert service.has_errors()
        assert "Нет прав" in service.get_errors()[0]
        mailing.refresh_from_db()
        assert mailing.recipients.count() == 0

    @pytest.mark.django_db
    def test_remove_recipients_unauthorized(self, user, another_user):
        """Проверка: другой пользователь не может удалять получателей из чужой рассылки"""
        service = MailingService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        recipient = Recipient.objects.create(email="r1@example.com", full_name="R1", owner=user)

        mailing.recipients.add(recipient)
        assert mailing.recipients.count() == 1

        # Попытка другого пользователя удалить получателей
        result = service.remove_recipients(mailing.id, [recipient.id], user=another_user)

        assert result is None
        assert service.has_errors()
        assert "Нет прав" in service.get_errors()[0]
        mailing.refresh_from_db()
        assert mailing.recipients.count() == 1

    @pytest.mark.django_db
    def test_add_recipients_to_nonexistent_mailing(self, user):
        """Проверка: добавление получателей к несуществующей рассылке возвращает None"""
        service = MailingService()

        recipient = Recipient.objects.create(email="r1@example.com", full_name="R1", owner=user)

        result = service.add_recipients(999, [recipient.id], user=user)

        assert result is None
        assert service.has_errors()
        assert "не найдена" in service.get_errors()[0]

    @pytest.mark.django_db
    def test_remove_recipients_from_nonexistent_mailing(self, user):
        """Проверка: удаление получателей из несуществующей рассылки возвращает None"""
        service = MailingService()

        recipient = Recipient.objects.create(email="r1@example.com", full_name="R1", owner=user)

        result = service.remove_recipients(999, [recipient.id], user=user)

        assert result is None
        assert service.has_errors()
        assert "не найдена" in service.get_errors()[0]

    @pytest.mark.django_db
    def test_get_active_mailings(self, user):
        """Проверка: получение активных (запущенных) рассылок"""
        service = MailingService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        # Создаем запущенную рассылку
        running = Mailing.objects.create(
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(days=1),
            message=message,
            owner=user,
            status=Mailing.STATUS_RUNNING,
        )

        # Создаем созданную рассылку
        created = Mailing.objects.create(
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(days=1),
            message=message,
            owner=user,
            status=Mailing.STATUS_CREATED,
        )

        # Получаем только запущенные
        active_mailings = service.get_active_mailings(user=user)

        assert running in active_mailings
        assert created not in active_mailings
        assert active_mailings.count() == 1


class TestAttemptService:
    """Тесты для AttemptService"""

    @pytest.mark.django_db
    def test_create_attempt(self, user):
        """Проверка: создание попытки отправки"""
        service = AttemptService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        attempt = service.create(
            data={
                "mailing": mailing,
                "recipient": recipient,
                "status": Attempt.STATUS_SUCCESS,
                "server_response": "250 OK",
            }
        )

        assert attempt.mailing == mailing
        assert attempt.recipient == recipient
        assert attempt.status == Attempt.STATUS_SUCCESS
        assert attempt.server_response == "250 OK"

    @pytest.mark.django_db
    def test_get_attempts_for_mailing(self, user):
        """Проверка: получение всех попыток для рассылки"""
        service = AttemptService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        a1 = Attempt.objects.create(mailing=mailing, recipient=recipient, status=Attempt.STATUS_SUCCESS)

        a2 = Attempt.objects.create(mailing=mailing, recipient=recipient, status=Attempt.STATUS_FAILURE)

        attempts = service.get_for_mailing(mailing.id)

        assert a1 in attempts
        assert a2 in attempts
        assert attempts.count() == 2

    @pytest.mark.django_db
    def test_get_successful_attempts(self, user):
        """Проверка: получение успешных попыток для рассылки"""
        service = AttemptService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        success = Attempt.objects.create(
            mailing=mailing, recipient=recipient, status=Attempt.STATUS_SUCCESS, server_response="250 OK"
        )

        failure = Attempt.objects.create(
            mailing=mailing, recipient=recipient, status=Attempt.STATUS_FAILURE, server_response="550 Error"
        )

        successful_attempts = service.get_successful(mailing.id)

        assert success in successful_attempts
        assert failure not in successful_attempts
        assert successful_attempts.count() == 1

    @pytest.mark.django_db
    def test_get_failed_attempts(self, user):
        """Проверка: получение неудачных попыток для рассылки"""
        service = AttemptService()

        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        success = Attempt.objects.create(
            mailing=mailing, recipient=recipient, status=Attempt.STATUS_SUCCESS, server_response="250 OK"
        )

        failure = Attempt.objects.create(
            mailing=mailing, recipient=recipient, status=Attempt.STATUS_FAILURE, server_response="550 Error"
        )

        failed_attempts = service.get_failed(mailing.id)

        assert failure in failed_attempts
        assert success not in failed_attempts
        assert failed_attempts.count() == 1
