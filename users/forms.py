from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    """Форма для входа в систему"""
    
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "email@example.com",
                "autofocus": True
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "********"
            }
        )
    )


class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации нового пользователя"""
    
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "email@example.com"
            }
        ),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "********"
            }
        )
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "********"
            }
        ),
    )
    
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
    
    def clean_email(self):
        """Валидация email"""
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Пользователь с таким email уже зарегистрирован."
                )
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"]
        user.email = email
        user.username = email
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "avatar", "phone", "country"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "email@example.com"
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Имя"
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Фамилия"
                }
            ),
            "avatar": forms.FileInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+7 (999) 123-45-67"
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Россия"
                }
            ),
        }
        labels = {
            "email": "Email",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "avatar": "Аватар",
            "phone": "Телефон",
            "country": "Страна",
        }
