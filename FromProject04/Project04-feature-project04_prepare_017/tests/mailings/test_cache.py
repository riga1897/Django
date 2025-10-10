"""
Тесты для кеширования и инвалидации кеша.

TDD подход: RED-GREEN-REFACTOR
Эти тесты должны провалиться до реализации signals.
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from apps.mailings.models import Mailing, Message, Recipient

User = get_user_model()


@pytest.fixture
def user(db):
    """Создаёт тестового пользователя"""
    user = User.objects.create_user(email="test@example.com", password="testpass123")
    user.is_email_verified = True
    user.save()
    return user


@pytest.fixture
def message(user):
    """Создаёт тестовое сообщение"""
    return Message.objects.create(subject="Test Subject", body="Test Body", owner=user)


@pytest.mark.django_db
class TestCacheInvalidation:
    """Тесты инвалидации кеша при изменении данных"""

    def test_mailing_create_invalidates_cache(self, user, message):
        """При создании рассылки кеш пользователя должен инвалидироваться"""
        # Устанавливаем кеш для пользователя
        cache_key = f"user_{user.id}_total_mailings"
        cache.set(cache_key, 999, timeout=300)

        # Проверяем что кеш установлен
        assert cache.get(cache_key) == 999

        # Создаём рассылку
        now = timezone.now()
        Mailing.objects.create(
            message=message,
            status=Mailing.STATUS_CREATED,
            start_datetime=now,
            end_datetime=now + timedelta(days=1),
            owner=user,
        )

        # Кеш должен быть инвалидирован (удалён)
        assert cache.get(cache_key) is None

    def test_mailing_delete_invalidates_cache(self, user, message):
        """При удалении рассылки кеш пользователя должен инвалидироваться"""
        # Создаём рассылку
        now = timezone.now()
        mailing = Mailing.objects.create(
            message=message,
            status=Mailing.STATUS_CREATED,
            start_datetime=now,
            end_datetime=now + timedelta(days=1),
            owner=user,
        )

        # Устанавливаем кеш
        cache_key = f"user_{user.id}_total_mailings"
        cache.set(cache_key, 1, timeout=300)
        assert cache.get(cache_key) == 1

        # Удаляем рассылку
        mailing.delete()

        # Кеш должен быть инвалидирован
        assert cache.get(cache_key) is None

    def test_mailing_update_invalidates_cache(self, user, message):
        """При изменении рассылки кеш пользователя должен инвалидироваться"""
        # Создаём рассылку
        now = timezone.now()
        mailing = Mailing.objects.create(
            message=message,
            status=Mailing.STATUS_CREATED,
            start_datetime=now,
            end_datetime=now + timedelta(days=1),
            owner=user,
        )

        # Устанавливаем кеш
        cache_key = f"user_{user.id}_active_mailings"
        cache.set(cache_key, 5, timeout=300)
        assert cache.get(cache_key) == 5

        # Изменяем статус рассылки
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save()

        # Кеш должен быть инвалидирован
        assert cache.get(cache_key) is None

    def test_recipient_create_invalidates_cache(self, user):
        """При создании получателя кеш пользователя должен инвалидироваться"""
        # Устанавливаем кеш
        cache_key = f"user_{user.id}_unique_recipients"
        cache.set(cache_key, 10, timeout=300)
        assert cache.get(cache_key) == 10

        # Создаём получателя
        Recipient.objects.create(email="recipient@example.com", full_name="Test Recipient", owner=user)

        # Кеш должен быть инвалидирован
        assert cache.get(cache_key) is None

    def test_recipient_delete_invalidates_cache(self, user):
        """При удалении получателя кеш пользователя должен инвалидироваться"""
        # Создаём получателя
        recipient = Recipient.objects.create(email="recipient@example.com", full_name="Test Recipient", owner=user)

        # Устанавливаем кеш
        cache_key = f"user_{user.id}_unique_recipients"
        cache.set(cache_key, 1, timeout=300)
        assert cache.get(cache_key) == 1

        # Удаляем получателя
        recipient.delete()

        # Кеш должен быть инвалидирован
        assert cache.get(cache_key) is None

    def test_message_changes_invalidate_cache(self, user):
        """При создании/удалении сообщения кеш НЕ инвалидируется (сообщения не влияют на статистику)"""
        # Устанавливаем кеш
        cache_key = f"user_{user.id}_total_mailings"
        cache.set(cache_key, 5, timeout=300)

        # Создаём сообщение
        message = Message.objects.create(subject="Test", body="Test body", owner=user)

        # Кеш НЕ должен быть инвалидирован (сообщения не влияют на статистику главной)
        assert cache.get(cache_key) == 5

        # Удаляем сообщение
        message.delete()

        # Кеш всё ещё НЕ должен быть инвалидирован
        assert cache.get(cache_key) == 5

    def test_mailing_owner_change_invalidates_both_users_cache(self, db):
        """При изменении owner рассылки кеш инвалидируется для обоих пользователей"""
        # Создаём двух пользователей
        user1 = User.objects.create_user(email="user1@test.com", password="pass")
        user2 = User.objects.create_user(email="user2@test.com", password="pass")

        # Создаём сообщение и рассылку для user1
        message = Message.objects.create(subject="Test", body="Body", owner=user1)
        now = timezone.now()
        mailing = Mailing.objects.create(
            message=message,
            status=Mailing.STATUS_CREATED,
            start_datetime=now,
            end_datetime=now + timedelta(days=1),
            owner=user1,
        )

        # Устанавливаем кеш для обоих пользователей
        cache.set(f"user_{user1.id}_total_mailings", 10, timeout=300)
        cache.set(f"user_{user2.id}_total_mailings", 5, timeout=300)

        # Проверяем что кеш установлен
        assert cache.get(f"user_{user1.id}_total_mailings") == 10
        assert cache.get(f"user_{user2.id}_total_mailings") == 5

        # Изменяем owner рассылки
        mailing.owner = user2
        mailing.save()

        # Кеш должен быть инвалидирован для ОБОИХ пользователей
        assert cache.get(f"user_{user1.id}_total_mailings") is None
        assert cache.get(f"user_{user2.id}_total_mailings") is None

    def test_recipient_owner_change_invalidates_both_users_cache(self, db):
        """При изменении owner получателя кеш инвалидируется для обоих пользователей"""
        # Создаём двух пользователей
        user1 = User.objects.create_user(email="user1@test.com", password="pass")
        user2 = User.objects.create_user(email="user2@test.com", password="pass")

        # Создаём получателя для user1
        recipient = Recipient.objects.create(email="recipient@test.com", full_name="Test Recipient", owner=user1)

        # Устанавливаем кеш для обоих пользователей
        cache.set(f"user_{user1.id}_unique_recipients", 10, timeout=300)
        cache.set(f"user_{user2.id}_unique_recipients", 5, timeout=300)

        # Проверяем что кеш установлен
        assert cache.get(f"user_{user1.id}_unique_recipients") == 10
        assert cache.get(f"user_{user2.id}_unique_recipients") == 5

        # Изменяем owner получателя
        recipient.owner = user2
        recipient.save()

        # Кеш должен быть инвалидирован для ОБОИХ пользователей
        assert cache.get(f"user_{user1.id}_unique_recipients") is None
        assert cache.get(f"user_{user2.id}_unique_recipients") is None


@pytest.mark.django_db
class TestHomeViewCaching:
    """Тесты кеширования в home view"""

    def test_home_statistics_are_cached(self, client, user, message):
        """Статистика на главной странице должна кешироваться"""
        client.force_login(user)

        # Создаём данные
        now = timezone.now()
        Mailing.objects.create(
            message=message,
            status=Mailing.STATUS_CREATED,
            start_datetime=now,
            end_datetime=now + timedelta(days=1),
            owner=user,
        )
        Recipient.objects.create(email="test@example.com", full_name="Test", owner=user)

        # Первый запрос - данные из БД
        response1 = client.get("/")
        assert response1.status_code == 200
        assert response1.context["total_mailings"] == 1
        assert response1.context["unique_recipients"] == 1

        # Проверяем что кеш установлен
        cache_key_mailings = f"user_{user.id}_total_mailings"
        cache_key_recipients = f"user_{user.id}_unique_recipients"

        assert cache.get(cache_key_mailings) is not None
        assert cache.get(cache_key_recipients) is not None

        # Второй запрос - данные из кеша (не из БД)
        response2 = client.get("/")
        assert response2.status_code == 200
        assert response2.context["total_mailings"] == 1
        assert response2.context["unique_recipients"] == 1

    def test_cache_is_user_specific(self, client, message):
        """Кеш должен быть специфичен для каждого пользователя"""
        # Создаём двух пользователей
        user1 = User.objects.create_user(email="user1@example.com", password="pass")
        user1.is_email_verified = True
        user1.save()
        user2 = User.objects.create_user(email="user2@example.com", password="pass")
        user2.is_email_verified = True
        user2.save()

        # Создаём рассылку для user1
        message1 = Message.objects.create(subject="Test", body="Body", owner=user1)
        now = timezone.now()
        Mailing.objects.create(
            message=message1,
            status=Mailing.STATUS_CREATED,
            start_datetime=now,
            end_datetime=now + timedelta(days=1),
            owner=user1,
        )

        # User1 заходит на главную
        client.force_login(user1)
        response1 = client.get("/")
        assert response1.context["total_mailings"] == 1

        # User2 заходит на главную
        client.force_login(user2)
        response2 = client.get("/")
        assert response2.context["total_mailings"] == 0  # У user2 нет рассылок

        # Проверяем что у каждого свой кеш
        cache_key1 = f"user_{user1.id}_total_mailings"
        cache_key2 = f"user_{user2.id}_total_mailings"

        assert cache.get(cache_key1) == 1
        assert cache.get(cache_key2) == 0
