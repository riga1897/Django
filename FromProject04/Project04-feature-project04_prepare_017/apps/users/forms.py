from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    """Форма для входа в систему"""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "email@example.com", "autofocus": True}
        ),
    )
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "********"})
    )


class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации нового пользователя"""

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
    )
    password1 = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "********"})
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "********"}),
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        """Валидация email с проверкой неподтвержденных пользователей"""
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()

            # Проверяем, существует ли пользователь с таким email
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                # Если пользователь уже подтвержден или активен - блокируем регистрацию
                if existing_user.is_email_verified or existing_user.is_active:  # type: ignore[attr-defined]
                    raise forms.ValidationError(
                        "Пользователь с таким email уже зарегистрирован. "
                        "Если вы забыли пароль, воспользуйтесь восстановлением пароля."
                    )
                else:
                    # Для неподтвержденного пользователя проверяем возраст токена
                    token_age_limit = timezone.now() - timedelta(hours=24)

                    # Если токен старше 24 часов или не был создан - удаляем старую запись
                    if not existing_user.token_created_at or existing_user.token_created_at < token_age_limit:  # type: ignore[attr-defined]
                        # Безопасно удаляем старую неподтвержденную регистрацию
                        # (каскадное удаление очистит связанные записи)
                        existing_user.delete()
                    else:
                        # Токен еще свежий - просим подождать
                        raise forms.ValidationError(
                            "На этот email уже отправлено письмо для подтверждения регистрации. "
                            'Пожалуйста, проверьте свою почту (включая папку "Спам"). '
                            "Если письмо не пришло, попробуйте зарегистрироваться через 24 часа."
                        )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"]
        user.email = email
        # ВАЖНО: устанавливаем username = email для уникальности
        user.username = email
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""

    class Meta:
        model = User
        fields = ["email", "avatar", "phone", "country"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+7 (999) 123-45-67"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Россия"}),
        }
        labels = {
            "email": "Email",
            "avatar": "Аватар",
            "phone": "Телефон",
            "country": "Страна",
        }
