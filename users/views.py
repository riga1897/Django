from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, UpdateView

from users.forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm
from users.models import User


class UserLoginView(LoginView):
    """Вход пользователя через модальное окно"""

    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        """Редирект на главную при попытке GET запроса"""
        from django.shortcuts import redirect
        return redirect("marketplace:products_list")

    def get_redirect_url(self):
        """Безопасный редирект после успешного входа"""
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return str(reverse_lazy("marketplace:products_list"))

    def form_invalid(self, form):
        """При ошибке редирект обратно с параметром для открытия модалки"""
        from django.shortcuts import redirect
        next_url = self.request.POST.get("next", "/")
        
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            next_url = "/"
        
        messages.error(
            self.request,
            "Неверный email или пароль. Попробуйте еще раз."
        )
        
        query_params = {"show_login_modal": "1"}
        if next_url and next_url != "/":
            query_params["next"] = next_url
        
        return redirect(f"/?{urlencode(query_params)}")


class UserLogoutView(LogoutView):
    """Выход пользователя"""

    def get_default_redirect_url(self):
        return str(reverse_lazy("marketplace:product_list"))


class UserRegisterView(CreateView):
    """Регистрация нового пользователя через модальное окно"""

    model = User
    form_class = CustomUserCreationForm

    def get(self, request, *args, **kwargs):
        """Редирект на главную при попытке GET запроса"""
        from django.shortcuts import redirect
        return redirect("marketplace:products_list")

    def get_success_url(self):
        """Безопасный редирект после успешной регистрации"""
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return str(reverse_lazy("marketplace:products_list"))

    def form_valid(self, form):
        """Успешная регистрация - автоматический вход"""
        from django.contrib.auth import login
        user = form.save()
        self.send_welcome_email(user.email)
        login(self.request, user)
        messages.success(
            self.request,
            "Добро пожаловать! Регистрация прошла успешно."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """При ошибке редирект обратно с параметром для открытия модалки"""
        from django.shortcuts import redirect
        next_url = self.request.POST.get("next", "/")
        
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            next_url = "/"
        
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(error)
        messages.error(
            self.request,
            " ".join(error_messages) if error_messages else "Ошибка регистрации. Проверьте введенные данные."
        )
        
        query_params = {"show_register_modal": "1"}
        if next_url and next_url != "/":
            query_params["next"] = next_url
        
        return redirect(f"/?{urlencode(query_params)}")

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
