"""
Тесты для форм приложения users.

Проверяем:
- CustomAuthenticationForm
- CustomUserCreationForm
- UserProfileForm
"""

import pytest
from django.contrib.auth import get_user_model

from apps.users.forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm

User = get_user_model()


class TestCustomAuthenticationForm:
    """Тесты для формы входа в систему"""

    @pytest.mark.django_db
    def test_form_valid_with_correct_credentials(self, user):
        """Проверка: форма валидна при корректных данных"""
        form = CustomAuthenticationForm(
            data={
                "username": "user@example.com",
                "password": "testpassword123",
            }
        )

        assert form.is_valid()
        assert form.errors == {}

    @pytest.mark.django_db
    def test_form_invalid_with_wrong_password(self, user):
        """Проверка: форма невалидна при неверном пароле"""
        form = CustomAuthenticationForm(
            data={
                "username": "user@example.com",
                "password": "wrongpassword",
            }
        )

        assert not form.is_valid()
        assert "username" not in form.errors or "__all__" in form.errors

    @pytest.mark.django_db
    def test_form_invalid_with_nonexistent_email(self):
        """Проверка: форма невалидна при несуществующем email"""
        form = CustomAuthenticationForm(
            data={
                "username": "nonexistent@example.com",
                "password": "somepassword",
            }
        )

        assert not form.is_valid()

    @pytest.mark.django_db
    def test_form_invalid_without_email(self):
        """Проверка: форма невалидна без email"""
        form = CustomAuthenticationForm(
            data={
                "username": "",
                "password": "testpassword123",
            }
        )

        assert not form.is_valid()
        assert "username" in form.errors

    @pytest.mark.django_db
    def test_form_invalid_without_password(self):
        """Проверка: форма невалидна без пароля"""
        form = CustomAuthenticationForm(
            data={
                "username": "user@example.com",
                "password": "",
            }
        )

        assert not form.is_valid()
        assert "password" in form.errors

    def test_email_field_has_bootstrap_class(self):
        """Проверка: поле email имеет Bootstrap класс"""
        form = CustomAuthenticationForm()
        assert "form-control" in form.fields["username"].widget.attrs["class"]

    def test_password_field_has_bootstrap_class(self):
        """Проверка: поле password имеет Bootstrap класс"""
        form = CustomAuthenticationForm()
        assert "form-control" in form.fields["password"].widget.attrs["class"]


class TestCustomUserCreationForm:
    """Тесты для формы регистрации пользователя"""

    @pytest.mark.django_db
    def test_form_valid_with_correct_data(self):
        """Проверка: форма валидна при корректных данных"""
        form = CustomUserCreationForm(
            data={
                "email": "newuser@example.com",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            }
        )

        assert form.is_valid()
        assert form.errors == {}

    @pytest.mark.django_db
    def test_form_invalid_with_mismatched_passwords(self):
        """Проверка: форма невалидна при несовпадающих паролях"""
        form = CustomUserCreationForm(
            data={
                "email": "newuser@example.com",
                "password1": "password123",
                "password2": "differentpassword",
            }
        )

        assert not form.is_valid()
        assert "password2" in form.errors

    @pytest.mark.django_db
    def test_form_invalid_with_duplicate_email(self, user):
        """Проверка: форма невалидна при дублирующемся email"""
        form = CustomUserCreationForm(
            data={
                "email": "user@example.com",  # уже существует
                "password1": "password123",
                "password2": "password123",
            }
        )

        assert not form.is_valid()
        assert "email" in form.errors

    @pytest.mark.django_db
    def test_form_invalid_without_email(self):
        """Проверка: форма невалидна без email"""
        form = CustomUserCreationForm(
            data={
                "email": "",
                "password1": "password123",
                "password2": "password123",
            }
        )

        assert not form.is_valid()
        assert "email" in form.errors

    @pytest.mark.django_db
    def test_form_invalid_with_weak_password(self):
        """Проверка: форма невалидна при слабом пароле"""
        form = CustomUserCreationForm(
            data={
                "email": "newuser@example.com",
                "password1": "123",
                "password2": "123",
            }
        )

        assert not form.is_valid()
        assert "password2" in form.errors or "password1" in form.errors

    @pytest.mark.django_db
    def test_save_creates_user_with_email(self):
        """Проверка: save() создает пользователя с email"""
        form = CustomUserCreationForm(
            data={
                "email": "newuser@example.com",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            }
        )

        assert form.is_valid()
        user = form.save()

        assert user.email == "newuser@example.com"
        assert user.check_password("strongpassword123")

    @pytest.mark.django_db
    def test_save_with_commit_false(self):
        """Проверка: save(commit=False) не сохраняет в БД"""
        form = CustomUserCreationForm(
            data={
                "email": "newuser@example.com",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            }
        )

        assert form.is_valid()
        user = form.save(commit=False)

        assert user.email == "newuser@example.com"
        assert user.pk is None  # не сохранен в БД

    def test_email_field_has_bootstrap_class(self):
        """Проверка: поле email имеет Bootstrap класс"""
        form = CustomUserCreationForm()
        assert "form-control" in form.fields["email"].widget.attrs["class"]

    def test_password1_field_has_bootstrap_class(self):
        """Проверка: поле password1 имеет Bootstrap класс"""
        form = CustomUserCreationForm()
        assert "form-control" in form.fields["password1"].widget.attrs["class"]

    def test_password2_field_has_bootstrap_class(self):
        """Проверка: поле password2 имеет Bootstrap класс"""
        form = CustomUserCreationForm()
        assert "form-control" in form.fields["password2"].widget.attrs["class"]


class TestUserProfileForm:
    """Тесты для формы редактирования профиля"""

    @pytest.mark.django_db
    def test_form_valid_with_correct_data(self, user):
        """Проверка: форма валидна при корректных данных"""
        form = UserProfileForm(
            instance=user,
            data={
                "email": "updated@example.com",
                "phone": "+79001234567",
                "country": "Russia",
            },
        )

        assert form.is_valid()
        assert form.errors == {}

    @pytest.mark.django_db
    def test_form_saves_updated_data(self, user):
        """Проверка: форма сохраняет обновленные данные"""
        form = UserProfileForm(
            instance=user,
            data={
                "email": "updated@example.com",
                "phone": "+79001234567",
                "country": "Russia",
            },
        )

        assert form.is_valid()
        updated_user = form.save()

        assert updated_user.email == "updated@example.com"
        assert updated_user.phone == "+79001234567"
        assert updated_user.country == "Russia"

    @pytest.mark.django_db
    def test_form_has_all_fields(self):
        """Проверка: форма содержит все необходимые поля"""
        form = UserProfileForm()

        assert "email" in form.fields
        assert "avatar" in form.fields
        assert "phone" in form.fields
        assert "country" in form.fields

    def test_email_field_has_bootstrap_class(self):
        """Проверка: поле email имеет Bootstrap класс"""
        form = UserProfileForm()
        assert "form-control" in form.fields["email"].widget.attrs["class"]

    def test_phone_field_has_bootstrap_class(self):
        """Проверка: поле phone имеет Bootstrap класс"""
        form = UserProfileForm()
        assert "form-control" in form.fields["phone"].widget.attrs["class"]

    def test_country_field_has_bootstrap_class(self):
        """Проверка: поле country имеет Bootstrap класс"""
        form = UserProfileForm()
        assert "form-control" in form.fields["country"].widget.attrs["class"]

    def test_avatar_field_has_bootstrap_class(self):
        """Проверка: поле avatar имеет Bootstrap класс"""
        form = UserProfileForm()
        assert "form-control" in form.fields["avatar"].widget.attrs["class"]

    @pytest.mark.django_db
    def test_form_invalid_with_duplicate_email(self, user, another_user):
        """Проверка: форма невалидна при попытке использовать чужой email"""
        form = UserProfileForm(
            instance=user,
            data={
                "email": "another@example.com",  # email другого пользователя
                "phone": "+79001234567",
                "country": "Russia",
            },
        )

        assert not form.is_valid()
        assert "email" in form.errors
