"""
Тесты для форм приложения mailings.

Проверяем:
- RecipientForm
- MessageForm
- MailingForm
- MailingUpdateForm
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.mailings.forms import MailingForm, MailingUpdateForm, MessageForm, RecipientForm
from apps.mailings.models import Message, Recipient

User = get_user_model()


@pytest.fixture
def user(db):
    """Фикстура для создания пользователя"""
    return User.objects.create_user(email="owner@example.com", password="testpass123", username="owner")


@pytest.fixture
def another_user(db):
    """Фикстура для создания другого пользователя"""
    return User.objects.create_user(email="another@example.com", password="testpass123", username="another")


@pytest.fixture
def recipient(user):
    """Фикстура для создания получателя"""
    return Recipient.objects.create(email="recipient@example.com", full_name="John Doe", owner=user)


@pytest.fixture
def another_recipient(another_user):
    """Фикстура для создания получателя другого пользователя"""
    return Recipient.objects.create(email="another_recipient@example.com", full_name="Jane Smith", owner=another_user)


@pytest.fixture
def message(user):
    """Фикстура для создания сообщения"""
    return Message.objects.create(subject="Test Subject", body="Test Body", owner=user)


@pytest.fixture
def another_message(another_user):
    """Фикстура для создания сообщения другого пользователя"""
    return Message.objects.create(subject="Another Subject", body="Another Body", owner=another_user)


class TestRecipientForm:
    """Тесты для формы получателя"""

    @pytest.mark.django_db
    def test_form_valid_with_correct_data(self):
        """Проверка: форма валидна при корректных данных"""
        form = RecipientForm(
            data={
                "email": "new@example.com",
                "full_name": "New Recipient",
                "comment": "Test comment",
            }
        )

        assert form.is_valid()
        assert form.errors == {}

    @pytest.mark.django_db
    def test_form_saves_data(self, user):
        """Проверка: форма сохраняет данные"""
        form = RecipientForm(
            data={
                "email": "new@example.com",
                "full_name": "New Recipient",
                "comment": "Test comment",
            }
        )

        assert form.is_valid()
        recipient = form.save(commit=False)
        recipient.owner = user
        recipient.save()

        assert recipient.email == "new@example.com"
        assert recipient.full_name == "New Recipient"
        assert recipient.comment == "Test comment"

    @pytest.mark.django_db
    def test_form_invalid_without_email(self):
        """Проверка: форма невалидна без email"""
        form = RecipientForm(
            data={
                "email": "",
                "full_name": "New Recipient",
            }
        )

        assert not form.is_valid()
        assert "email" in form.errors

    @pytest.mark.django_db
    def test_form_invalid_without_full_name(self):
        """Проверка: форма невалидна без full_name"""
        form = RecipientForm(
            data={
                "email": "new@example.com",
                "full_name": "",
            }
        )

        assert not form.is_valid()
        assert "full_name" in form.errors

    def test_form_has_all_fields(self):
        """Проверка: форма содержит все необходимые поля"""
        form = RecipientForm()

        assert "email" in form.fields
        assert "full_name" in form.fields
        assert "comment" in form.fields

    def test_email_field_has_bootstrap_class(self):
        """Проверка: поле email имеет Bootstrap класс"""
        form = RecipientForm()
        assert "form-control" in form.fields["email"].widget.attrs["class"]

    def test_full_name_field_has_bootstrap_class(self):
        """Проверка: поле full_name имеет Bootstrap класс"""
        form = RecipientForm()
        assert "form-control" in form.fields["full_name"].widget.attrs["class"]

    def test_comment_field_has_bootstrap_class(self):
        """Проверка: поле comment имеет Bootstrap класс"""
        form = RecipientForm()
        assert "form-control" in form.fields["comment"].widget.attrs["class"]


class TestMessageForm:
    """Тесты для формы сообщения"""

    @pytest.mark.django_db
    def test_form_valid_with_correct_data(self):
        """Проверка: форма валидна при корректных данных"""
        form = MessageForm(
            data={
                "subject": "Test Subject",
                "body": "Test Body",
            }
        )

        assert form.is_valid()
        assert form.errors == {}

    @pytest.mark.django_db
    def test_form_saves_data(self, user):
        """Проверка: форма сохраняет данные"""
        form = MessageForm(
            data={
                "subject": "Test Subject",
                "body": "Test Body",
            }
        )

        assert form.is_valid()
        message = form.save(commit=False)
        message.owner = user
        message.save()

        assert message.subject == "Test Subject"
        assert message.body == "Test Body"

    @pytest.mark.django_db
    def test_form_invalid_without_subject(self):
        """Проверка: форма невалидна без subject"""
        form = MessageForm(
            data={
                "subject": "",
                "body": "Test Body",
            }
        )

        assert not form.is_valid()
        assert "subject" in form.errors

    @pytest.mark.django_db
    def test_form_invalid_without_body(self):
        """Проверка: форма невалидна без body"""
        form = MessageForm(
            data={
                "subject": "Test Subject",
                "body": "",
            }
        )

        assert not form.is_valid()
        assert "body" in form.errors

    def test_form_has_all_fields(self):
        """Проверка: форма содержит все необходимые поля"""
        form = MessageForm()

        assert "subject" in form.fields
        assert "body" in form.fields

    def test_subject_field_has_bootstrap_class(self):
        """Проверка: поле subject имеет Bootstrap класс"""
        form = MessageForm()
        assert "form-control" in form.fields["subject"].widget.attrs["class"]

    def test_body_field_has_bootstrap_class(self):
        """Проверка: поле body имеет Bootstrap класс"""
        form = MessageForm()
        assert "form-control" in form.fields["body"].widget.attrs["class"]


class TestMailingForm:
    """Тесты для формы рассылки"""

    @pytest.mark.django_db
    def test_form_valid_with_correct_data(self, user, message, recipient):
        """Проверка: форма валидна при корректных данных"""
        start = timezone.now()
        end = start + timedelta(days=1)

        form = MailingForm(
            data={
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
                "message": message.id,
                "recipients": [recipient.id],
            },
            user=user,
        )

        assert form.is_valid()
        assert form.errors == {}

    @pytest.mark.django_db
    def test_form_filters_messages_by_owner(self, user, message, another_message):
        """Проверка: форма фильтрует сообщения по владельцу"""
        form = MailingForm(user=user)

        # Только сообщения текущего пользователя
        message_ids = [m.id for m in form.fields["message"].queryset]
        assert message.id in message_ids
        assert another_message.id not in message_ids

    @pytest.mark.django_db
    def test_form_filters_recipients_by_owner(self, user, recipient, another_recipient):
        """Проверка: форма фильтрует получателей по владельцу"""
        form = MailingForm(user=user)

        # Только получатели текущего пользователя
        recipient_ids = [r.id for r in form.fields["recipients"].queryset]
        assert recipient.id in recipient_ids
        assert another_recipient.id not in recipient_ids

    @pytest.mark.django_db
    def test_form_without_user_shows_all(self, message, another_message):
        """Проверка: форма без user показывает все записи"""
        form = MailingForm()

        # Все сообщения доступны
        message_ids = [m.id for m in form.fields["message"].queryset]
        assert message.id in message_ids
        assert another_message.id in message_ids

    @pytest.mark.django_db
    def test_form_invalid_without_start_datetime(self, user, message, recipient):
        """Проверка: форма невалидна без start_datetime"""
        end = timezone.now() + timedelta(days=1)

        form = MailingForm(
            data={
                "start_datetime": "",
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
                "message": message.id,
                "recipients": [recipient.id],
            },
            user=user,
        )

        assert not form.is_valid()
        assert "start_datetime" in form.errors

    @pytest.mark.django_db
    def test_form_invalid_without_message(self, user, recipient):
        """Проверка: форма невалидна без message"""
        start = timezone.now()
        end = start + timedelta(days=1)

        form = MailingForm(
            data={
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
                "message": "",
                "recipients": [recipient.id],
            },
            user=user,
        )

        assert not form.is_valid()
        assert "message" in form.errors

    def test_form_has_all_fields(self, user):
        """Проверка: форма содержит все необходимые поля"""
        form = MailingForm(user=user)

        assert "start_datetime" in form.fields
        assert "end_datetime" in form.fields
        assert "message" in form.fields
        assert "recipients" in form.fields

    def test_start_datetime_field_has_bootstrap_class(self, user):
        """Проверка: поле start_datetime имеет Bootstrap класс"""
        form = MailingForm(user=user)
        assert "form-control" in form.fields["start_datetime"].widget.attrs["class"]

    def test_message_field_has_bootstrap_class(self, user):
        """Проверка: поле message имеет Bootstrap класс"""
        form = MailingForm(user=user)
        assert "form-select" in form.fields["message"].widget.attrs["class"]

    def test_recipients_field_has_bootstrap_class(self, user):
        """Проверка: поле recipients имеет Bootstrap класс"""
        form = MailingForm(user=user)
        assert "form-select" in form.fields["recipients"].widget.attrs["class"]


class TestMailingUpdateForm:
    """Тесты для формы редактирования рассылки"""

    @pytest.mark.django_db
    def test_form_has_status_field(self, user):
        """Проверка: форма содержит поле status"""
        form = MailingUpdateForm(user=user)

        assert "status" in form.fields

    @pytest.mark.django_db
    def test_form_valid_with_status(self, user, message, recipient):
        """Проверка: форма валидна с полем status"""
        start = timezone.now()
        end = start + timedelta(days=1)

        form = MailingUpdateForm(
            data={
                "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
                "status": "running",  # lowercase: created, running, completed
                "message": message.id,
                "recipients": [recipient.id],
            },
            user=user,
        )

        assert form.is_valid()
        assert form.errors == {}

    @pytest.mark.django_db
    def test_form_inherits_from_mailing_form(self, user):
        """Проверка: форма наследует от MailingForm"""
        form = MailingUpdateForm(user=user)

        # Проверяем что есть все поля от MailingForm
        assert "start_datetime" in form.fields
        assert "end_datetime" in form.fields
        assert "message" in form.fields
        assert "recipients" in form.fields
        # И добавлено новое поле
        assert "status" in form.fields

    def test_status_field_has_bootstrap_class(self, user):
        """Проверка: поле status имеет Bootstrap класс"""
        form = MailingUpdateForm(user=user)
        assert "form-select" in form.fields["status"].widget.attrs["class"]

    @pytest.mark.django_db
    def test_form_filters_by_owner_like_parent(self, user, message, another_message):
        """Проверка: форма фильтрует по владельцу как родительская"""
        form = MailingUpdateForm(user=user)

        # Только сообщения текущего пользователя
        message_ids = [m.id for m in form.fields["message"].queryset]
        assert message.id in message_ids
        assert another_message.id not in message_ids
