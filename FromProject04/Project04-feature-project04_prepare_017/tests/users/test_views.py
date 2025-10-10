"""
Тесты для views приложения users.

Проверяем:
- UserLoginView
- UserLogoutView
- UserRegisterView
- profile view
- ProfileUpdateView
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

User = get_user_model()


class TestUserLoginView:
    """Тесты для view входа в систему"""

    @pytest.mark.django_db
    def test_login_view_get_displays_form(self, client):
        """Проверка: GET запрос отображает форму входа"""
        url = reverse("login")
        response = client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert "users/login.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_login_view_post_with_valid_data(self, client, user):
        """Проверка: POST с валидными данными логинит и редиректит"""
        url = reverse("login")
        response = client.post(
            url,
            {
                "username": "user@example.com",
                "password": "testpassword123",
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("home")
        # Проверяем что пользователь залогинен
        assert "_auth_user_id" in client.session

    @pytest.mark.django_db
    def test_login_view_post_with_invalid_password(self, client, user):
        """Проверка: POST с неверным паролем показывает ошибки"""
        url = reverse("login")
        response = client.post(
            url,
            {
                "username": "user@example.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    @pytest.mark.django_db
    def test_login_view_post_with_nonexistent_email(self, client):
        """Проверка: POST с несуществующим email показывает ошибки"""
        url = reverse("login")
        response = client.post(
            url,
            {
                "username": "nonexistent@example.com",
                "password": "somepassword",
            },
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    @pytest.mark.django_db
    def test_login_view_redirects_authenticated_user(self, client, user):
        """Проверка: авторизованный пользователь редиректится с login page"""
        client.force_login(user)
        url = reverse("login")
        response = client.get(url)

        assert response.status_code == 302


class TestUserLogoutView:
    """Тесты для view выхода из системы"""

    @pytest.mark.django_db
    def test_logout_view_logs_out_user(self, client, user):
        """Проверка: logout разлогинивает пользователя"""
        client.force_login(user)
        url = reverse("logout")
        response = client.post(url)

        assert response.status_code == 302
        assert response.url == reverse("home")
        # Проверяем что пользователь разлогинен
        assert "_auth_user_id" not in client.session


class TestUserRegisterView:
    """Тесты для view регистрации"""

    @pytest.mark.django_db
    def test_register_view_get_displays_form(self, client):
        """Проверка: GET запрос отображает форму регистрации"""
        url = reverse("register")
        response = client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert "users/register.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_register_view_post_with_valid_data(self, client):
        """Проверка: POST с валидными данными создает пользователя и отправляет verification email"""
        url = reverse("register")
        response = client.post(
            url,
            {
                "email": "newuser@example.com",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            },
            follow=False,
        )

        assert response.status_code == 302
        assert response.url == reverse("email_verification_pending")

        # Проверяем что пользователь создан
        user = User.objects.get(email="newuser@example.com")
        assert user is not None
        assert user.is_active is False
        assert user.is_email_verified is False
        assert user.verification_token is not None
        assert user.token_created_at is not None

        # Проверяем success message
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert "почт" in str(messages[0]).lower()

    @pytest.mark.django_db
    def test_register_view_post_with_invalid_data(self, client):
        """Проверка: POST с невалидными данными показывает ошибки"""
        url = reverse("register")
        response = client.post(
            url,
            {
                "email": "newuser@example.com",
                "password1": "password123",
                "password2": "differentpassword",  # несовпадающие пароли
            },
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

        # Проверяем что пользователь НЕ создан
        assert not User.objects.filter(email="newuser@example.com").exists()

    @pytest.mark.django_db
    def test_register_view_post_with_duplicate_email(self, client, user):
        """Проверка: POST с существующим email показывает ошибки"""
        url = reverse("register")
        response = client.post(
            url,
            {
                "email": "user@example.com",  # уже существует
                "password1": "password123",
                "password2": "password123",
            },
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert "email" in response.context["form"].errors


class TestProfileView:
    """Тесты для view просмотра профиля"""

    @pytest.mark.django_db
    def test_profile_view_requires_login(self, client):
        """Проверка: profile требует авторизации"""
        url = reverse("profile")
        response = client.get(url)

        assert response.status_code == 302
        assert "/login/" in response.url

    @pytest.mark.django_db
    def test_profile_view_displays_user_profile(self, client, user):
        """Проверка: profile отображает профиль текущего пользователя"""
        client.force_login(user)
        url = reverse("profile")
        response = client.get(url)

        assert response.status_code == 200
        assert "user" in response.context
        assert response.context["user"] == user
        assert "users/profile.html" in [t.name for t in response.templates]


class TestProfileUpdateView:
    """Тесты для view редактирования профиля"""

    @pytest.mark.django_db
    def test_profile_edit_view_requires_login(self, client):
        """Проверка: profile_edit требует авторизации"""
        url = reverse("profile_edit")
        response = client.get(url)

        assert response.status_code == 302
        assert "/login/" in response.url

    @pytest.mark.django_db
    def test_profile_edit_view_get_displays_form(self, client, user):
        """Проверка: GET запрос отображает форму редактирования"""
        client.force_login(user)
        url = reverse("profile_edit")
        response = client.get(url)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["object"] == user
        assert "users/profile_edit.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_profile_edit_view_get_object_returns_current_user(self, client, user, another_user):
        """Проверка: get_object() возвращает текущего пользователя, а не другого"""
        client.force_login(user)
        url = reverse("profile_edit")
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["object"] == user
        assert response.context["object"] != another_user

    @pytest.mark.django_db
    def test_profile_edit_view_post_updates_profile(self, client, user):
        """Проверка: POST обновляет профиль текущего пользователя"""
        client.force_login(user)
        url = reverse("profile_edit")
        response = client.post(
            url,
            {
                "email": "updated@example.com",
                "phone": "+79001234567",
                "country": "Russia",
            },
            follow=False,
        )

        assert response.status_code == 302
        assert response.url == reverse("profile")

        # Проверяем что данные обновились
        user.refresh_from_db()
        assert user.email == "updated@example.com"
        assert user.phone == "+79001234567"
        assert user.country == "Russia"

    @pytest.mark.django_db
    def test_profile_edit_view_post_shows_success_message(self, client, user):
        """Проверка: POST показывает success message"""
        client.force_login(user)
        url = reverse("profile_edit")
        response = client.post(
            url,
            {
                "email": "updated@example.com",
                "phone": "+79001234567",
                "country": "Russia",
            },
            follow=True,
        )

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert "успешно" in str(messages[0]).lower()

    @pytest.mark.django_db
    def test_profile_edit_view_post_with_invalid_data(self, client, user, another_user):
        """Проверка: POST с невалидными данными показывает ошибки"""
        client.force_login(user)
        url = reverse("profile_edit")
        response = client.post(
            url,
            {
                "email": "another@example.com",  # email другого пользователя
                "phone": "+79001234567",
                "country": "Russia",
            },
        )

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

        # Проверяем что email НЕ изменился
        user.refresh_from_db()
        assert user.email == "user@example.com"

    @pytest.mark.django_db
    def test_profile_edit_view_does_not_allow_editing_other_users(self, client, user, another_user):
        """Проверка: пользователь не может редактировать профиль другого пользователя"""
        client.force_login(user)
        url = reverse("profile_edit")

        # Пытаемся обновить профиль - должен обновиться профиль текущего пользователя
        client.post(
            url,
            {
                "email": "hacked@example.com",
                "phone": "+79999999999",
                "country": "Hacked",
            },
        )

        # Проверяем что обновился профиль user, а не another_user
        user.refresh_from_db()
        another_user.refresh_from_db()

        assert user.email == "hacked@example.com"
        assert another_user.email == "another@example.com"  # не изменился
