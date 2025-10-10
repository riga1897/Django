from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm
from users.models import User


class UserLoginView(LoginView):
    """Вход пользователя"""

    template_name = "users/login.html"
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("marketplace:product_list")


class UserLogoutView(LogoutView):
    """Выход пользователя"""

    def get_default_redirect_url(self):
        return str(reverse_lazy("marketplace:product_list"))


class UserRegisterView(CreateView):
    """Регистрация нового пользователя"""

    model = User
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        self.send_welcome_email(user.email)
        messages.success(
            self.request,
            "Регистрация прошла успешно! Теперь вы можете войти в систему."
        )
        return super().form_valid(form)

    @staticmethod
    def send_welcome_email(user_email):
        subject = "Добро пожаловать в наш интернет-магазин!"
        message = "Спасибо, что зарегистрировались в нашем магазине!"
        from_email = "noreply@example.com"
        recipient_list = [user_email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception:
            pass


@login_required
def profile(request):
    """Просмотр профиля пользователя"""
    return render(request, "users/profile.html", {"user": request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""

    model = User
    template_name = "users/profile_edit.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен!")
        return super().form_valid(form)
