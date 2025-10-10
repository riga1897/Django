"""
Тесты для email verification функциональности.

Проверяем:
- Регистрация отправляет verification email
- Верификация с валидным токеном активирует пользователя
- Верификация с невалидным токеном показывает ошибку
- Верификация с просроченным токеном показывает ошибку
- Доступ к защищённым страницам блокируется без verification
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestEmailVerificationRegistration:
    """Тесты для регистрации с email verification"""

    def test_registration_sends_verification_email(self, client):
        """При регистрации отправляется письмо с подтверждением"""
        url = reverse("register")
        response = client.post(
            url,
            {
                "email": "newuser@example.com",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("email_verification_pending")

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == ["newuser@example.com"]
        assert "Подтверждение регистрации" in email.subject
        assert "verify-email" in email.body

    def test_registration_creates_inactive_user_with_token(self, client):
        """Регистрация создаёт неактивного пользователя с токеном"""
        url = reverse("register")
        client.post(
            url,
            {
                "email": "newuser@example.com",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            },
        )

        user = User.objects.get(email="newuser@example.com")
        assert user.is_active is False
        assert user.is_email_verified is False
        assert user.verification_token is not None
        assert user.token_created_at is not None

    def test_registration_token_is_uuid(self, client):
        """Токен верификации должен быть UUID"""
        url = reverse("register")
        client.post(
            url,
            {
                "email": "newuser@example.com",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            },
        )

        user = User.objects.get(email="newuser@example.com")
        assert len(user.verification_token) == 36
        assert user.verification_token.count("-") == 4


@pytest.mark.django_db
class TestEmailVerificationView:
    """Тесты для view подтверждения email"""

    def test_email_verification_with_valid_token_activates_user(self, client):
        """Подтверждение с валидным токеном активирует пользователя"""
        user = User.objects.create_user(email="test@example.com", password="testpass123", username="testuser")
        user.is_active = False
        user.is_email_verified = False
        user.verification_token = "test-token-123"
        user.token_created_at = timezone.now()
        user.save()

        url = reverse("email_verify", kwargs={"token": "test-token-123"})
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("login")

        user.refresh_from_db()
        assert user.is_active is True
        assert user.is_email_verified is True
        assert user.verification_token is None
        assert user.token_created_at is None

    def test_email_verification_with_invalid_token_shows_error(self, client):
        """Подтверждение с невалидным токеном показывает ошибку"""
        url = reverse("email_verify", kwargs={"token": "invalid-token"})
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("login")

    def test_email_verification_with_expired_token_shows_error(self, client):
        """Подтверждение с просроченным токеном показывает ошибку"""
        user = User.objects.create_user(email="test@example.com", password="testpass123", username="testuser")
        user.is_active = False
        user.is_email_verified = False
        user.verification_token = "test-token-123"
        user.token_created_at = timezone.now() - timedelta(days=2)
        user.save()

        url = reverse("email_verify", kwargs={"token": "test-token-123"})
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("register")

        user.refresh_from_db()
        assert user.is_active is False
        assert user.is_email_verified is False

    def test_email_verification_token_is_single_use(self, client):
        """Токен можно использовать только один раз"""
        user = User.objects.create_user(email="test@example.com", password="testpass123", username="testuser")
        user.is_active = False
        user.is_email_verified = False
        user.verification_token = "test-token-123"
        user.token_created_at = timezone.now()
        user.save()

        url = reverse("email_verify", kwargs={"token": "test-token-123"})
        client.get(url)

        response2 = client.get(url)
        assert response2.status_code == 302
        assert response2.url == reverse("login")


@pytest.mark.django_db
class TestAccessControlWithoutVerification:
    """Тесты для контроля доступа без email verification"""

    def test_unverified_user_cannot_access_home(self, client):
        """Непроверенный пользователь не может получить доступ к главной странице"""
        user = User.objects.create_user(email="test@example.com", password="testpass123", username="testuser")
        user.is_active = True
        user.is_email_verified = False
        user.save()

        client.force_login(user)
        response = client.get(reverse("home"))

        assert response.status_code == 302
        assert response.url == reverse("email_verification_pending")

    def test_unverified_user_cannot_access_profile(self, client):
        """Непроверенный пользователь не может получить доступ к профилю"""
        user = User.objects.create_user(email="test@example.com", password="testpass123", username="testuser")
        user.is_active = True
        user.is_email_verified = False
        user.save()

        client.force_login(user)
        response = client.get(reverse("profile"))

        assert response.status_code == 302
        assert response.url == reverse("email_verification_pending")

    def test_unverified_user_cannot_access_recipient_list(self, client):
        """Непроверенный пользователь не может получить доступ к списку получателей"""
        user = User.objects.create_user(email="test@example.com", password="testpass123", username="testuser")
        user.is_active = True
        user.is_email_verified = False
        user.save()

        client.force_login(user)
        response = client.get(reverse("recipient_list"))

        assert response.status_code == 302
        assert response.url == reverse("email_verification_pending")

    def test_verified_user_can_access_protected_pages(self, client, user):
        """Проверенный пользователь может получить доступ к защищённым страницам"""
        client.force_login(user)

        response_home = client.get(reverse("home"))
        response_profile = client.get(reverse("profile"))
        response_recipients = client.get(reverse("recipient_list"))

        assert response_home.status_code == 200
        assert response_profile.status_code == 200
        assert response_recipients.status_code == 200


@pytest.mark.django_db
class TestEmailVerificationPendingPage:
    """Тесты для страницы ожидания подтверждения email"""

    def test_email_verification_pending_page_displays(self, client):
        """Страница ожидания подтверждения отображается"""
        url = reverse("email_verification_pending")
        response = client.get(url)

        assert response.status_code == 200
        assert "users/email_verification_pending.html" in [t.name for t in response.templates]
