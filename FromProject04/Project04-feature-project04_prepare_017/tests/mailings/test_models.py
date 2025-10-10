"""
Тесты для моделей приложения mailings.

Проверяем:
- Recipient model
- Message model
- Mailing model
- Attempt model
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.mailings.models import Attempt, Mailing, Message, Recipient

User = get_user_model()


@pytest.fixture
def user(db):
    """Фикстура для создания пользователя"""
    return User.objects.create_user(email="owner@example.com", password="testpass123", username="owner")


@pytest.fixture
def another_user(db):
    """Фикстура для создания другого пользователя"""
    return User.objects.create_user(email="another@example.com", password="testpass123", username="another")


class TestRecipient:
    """Тесты для модели Recipient"""

    @pytest.mark.django_db
    def test_create_recipient(self, user):
        """Проверка: создание получателя"""
        recipient = Recipient.objects.create(
            email="recipient@example.com", full_name="John Doe", comment="Test recipient", owner=user
        )

        assert recipient.email == "recipient@example.com"
        assert recipient.full_name == "John Doe"
        assert recipient.comment == "Test recipient"
        assert recipient.owner == user

    @pytest.mark.django_db
    def test_recipient_str(self, user):
        """Проверка: __str__ возвращает имя и email"""
        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        assert str(recipient) == "Test User <test@example.com>"

    @pytest.mark.django_db
    def test_recipient_unique_together(self, user):
        """Проверка: email уникален в рамках одного owner"""
        Recipient.objects.create(email="test@example.com", full_name="User 1", owner=user)

        # Создание с тем же email и owner должно упасть
        from django.db import IntegrityError

        with pytest.raises(IntegrityError):
            Recipient.objects.create(email="test@example.com", full_name="User 2", owner=user)

    @pytest.mark.django_db
    def test_recipient_same_email_different_owners(self, user, another_user):
        """Проверка: один email может быть у разных owners"""
        r1 = Recipient.objects.create(email="test@example.com", full_name="User 1", owner=user)

        r2 = Recipient.objects.create(email="test@example.com", full_name="User 2", owner=another_user)

        assert r1.email == r2.email
        assert r1.owner != r2.owner

    @pytest.mark.django_db
    def test_recipient_inherits_owned_model(self, user):
        """Проверка: Recipient наследует от OwnedModel"""
        recipient = Recipient.objects.create(email="test@example.com", full_name="Test", owner=user)

        assert hasattr(recipient, "owner")
        assert hasattr(recipient, "is_active")
        assert hasattr(recipient, "created_at")
        assert hasattr(recipient, "updated_at")


class TestMessage:
    """Тесты для модели Message"""

    @pytest.mark.django_db
    def test_create_message(self, user):
        """Проверка: создание сообщения"""
        message = Message.objects.create(subject="Test Subject", body="Test body content", owner=user)

        assert message.subject == "Test Subject"
        assert message.body == "Test body content"
        assert message.owner == user

    @pytest.mark.django_db
    def test_message_str(self, user):
        """Проверка: __str__ возвращает subject"""
        message = Message.objects.create(subject="Newsletter #1", body="Body text", owner=user)

        assert str(message) == "Newsletter #1"

    @pytest.mark.django_db
    def test_message_inherits_owned_model(self, user):
        """Проверка: Message наследует от OwnedModel"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        assert hasattr(message, "owner")
        assert hasattr(message, "is_active")


class TestMailing:
    """Тесты для модели Mailing"""

    @pytest.mark.django_db
    def test_create_mailing(self, user):
        """Проверка: создание рассылки"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        assert mailing.message == message
        assert mailing.status == Mailing.STATUS_CREATED
        assert mailing.owner == user

    @pytest.mark.django_db
    def test_mailing_statuses(self, user):
        """Проверка: все статусы рассылки"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(days=1),
            message=message,
            owner=user,
            status=Mailing.STATUS_CREATED,
        )

        assert mailing.status == "created"
        assert mailing.get_status_display() == "Создана"

        mailing.status = Mailing.STATUS_RUNNING
        assert mailing.get_status_display() == "Запущена"

        mailing.status = Mailing.STATUS_COMPLETED
        assert mailing.get_status_display() == "Завершена"

    @pytest.mark.django_db
    def test_mailing_with_recipients(self, user):
        """Проверка: рассылка с получателями (M2M)"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient1 = Recipient.objects.create(email="r1@example.com", full_name="Recipient 1", owner=user)

        recipient2 = Recipient.objects.create(email="r2@example.com", full_name="Recipient 2", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        mailing.recipients.add(recipient1, recipient2)

        assert mailing.recipients.count() == 2
        assert recipient1 in mailing.recipients.all()
        assert recipient2 in mailing.recipients.all()

    @pytest.mark.django_db
    def test_mailing_str(self, user):
        """Проверка: __str__ включает subject и status"""
        message = Message.objects.create(subject="Newsletter", body="Body", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        assert "Newsletter" in str(mailing)
        assert "Создана" in str(mailing)

    @pytest.mark.django_db
    def test_mailing_meta_permissions(self):
        """Проверка: модель имеет кастомное разрешение"""
        permissions = [p[0] for p in Mailing._meta.permissions]
        assert "can_disable_mailing" in permissions


class TestAttempt:
    """Тесты для модели Attempt"""

    @pytest.mark.django_db
    def test_create_attempt(self, user):
        """Проверка: создание попытки отправки"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        attempt = Attempt.objects.create(
            mailing=mailing, recipient=recipient, status=Attempt.STATUS_SUCCESS, server_response="250 OK"
        )

        assert attempt.mailing == mailing
        assert attempt.recipient == recipient
        assert attempt.status == Attempt.STATUS_SUCCESS
        assert attempt.server_response == "250 OK"
        assert attempt.attempted_at is not None

    @pytest.mark.django_db
    def test_attempt_statuses(self, user):
        """Проверка: статусы попыток"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        success_attempt = Attempt.objects.create(mailing=mailing, recipient=recipient, status=Attempt.STATUS_SUCCESS)

        failure_attempt = Attempt.objects.create(
            mailing=mailing, recipient=recipient, status=Attempt.STATUS_FAILURE, server_response="500 Error"
        )

        assert success_attempt.get_status_display() == "Успешно"
        assert failure_attempt.get_status_display() == "Ошибка"

    @pytest.mark.django_db
    def test_attempt_str(self, user):
        """Проверка: __str__ включает статус и дату"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        attempt = Attempt.objects.create(mailing=mailing, recipient=recipient, status=Attempt.STATUS_SUCCESS)

        result = str(attempt)
        assert "Успешно" in result
        assert "Попытка" in result

    @pytest.mark.django_db
    def test_attempt_auto_datetime(self, user):
        """Проверка: attempted_at устанавливается автоматически"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        before = timezone.now()
        attempt = Attempt.objects.create(mailing=mailing, recipient=recipient, status=Attempt.STATUS_SUCCESS)
        after = timezone.now()

        assert before <= attempt.attempted_at <= after

    @pytest.mark.django_db
    def test_mailing_cascade_delete_attempts(self, user):
        """Проверка: при удалении Mailing удаляются Attempt"""
        message = Message.objects.create(subject="Test", body="Body", owner=user)

        recipient = Recipient.objects.create(email="test@example.com", full_name="Test User", owner=user)

        mailing = Mailing.objects.create(
            start_datetime=timezone.now(), end_datetime=timezone.now() + timedelta(days=1), message=message, owner=user
        )

        attempt = Attempt.objects.create(mailing=mailing, recipient=recipient, status=Attempt.STATUS_SUCCESS)

        attempt_id = attempt.id
        mailing.delete()

        assert not Attempt.objects.filter(id=attempt_id).exists()
