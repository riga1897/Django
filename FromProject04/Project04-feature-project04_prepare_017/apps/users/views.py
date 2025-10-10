import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, View

from apps.users.forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm
from apps.users.models import User


class EmailVerifiedRequiredMixin:
    """Mixin для проверки подтверждения email"""

    def dispatch(self, request, *args, **kwargs):  # type: ignore[override]
        if request.user.is_authenticated and not request.user.is_email_verified:
            return redirect("email_verification_pending")
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]


class UserLoginView(LoginView):
    """Вход пользователя"""

    template_name = "users/login.html"
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("home")


class UserLogoutView(LogoutView):
    """Выход пользователя"""

    def get_default_redirect_url(self):
        """Переопределяем метод вместо атрибута для избежания circular import"""
        return str(reverse_lazy("home"))


class UserRegisterView(CreateView):
    """Регистрация нового пользователя"""

    model = User
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("email_verification_pending")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.is_email_verified = False
        user.verification_token = str(uuid.uuid4())
        user.token_created_at = timezone.now()
        user.save()

        verification_url = self.request.build_absolute_uri(
            str(reverse_lazy("email_verify", kwargs={"token": user.verification_token}))
        )

        email_body = render_to_string(
            "emails/verify_email.html",
            {
                "user": user,
                "verification_url": verification_url,
            },
        )

        send_mail(
            subject="Подтверждение регистрации",
            message=f"Перейдите по ссылке для подтверждения: {verification_url}",
            from_email=None,
            recipient_list=[user.email],
            html_message=email_body,
        )

        self.object = user
        messages.success(self.request, "Регистрация прошла успешно! Проверьте вашу почту для подтверждения email.")
        return redirect(self.get_success_url())


@login_required
def profile(request):
    """Просмотр профиля пользователя"""
    if not request.user.is_email_verified:
        return redirect("email_verification_pending")
    return render(request, "users/profile.html", {"user": request.user})


class ProfileUpdateView(EmailVerifiedRequiredMixin, LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""

    model = User
    template_name = "users/profile_edit.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен!")
        return super().form_valid(form)


class EmailVerificationView(View):
    """Подтверждение email через токен"""

    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
        except User.DoesNotExist:
            messages.error(request, "Неверная ссылка подтверждения.")
            return redirect("login")

        if user.token_created_at:
            token_age = timezone.now() - user.token_created_at
            if token_age.total_seconds() > 24 * 60 * 60:
                messages.error(request, "Ссылка подтверждения истекла. Пожалуйста, зарегистрируйтесь снова.")
                return redirect("register")

        user.is_active = True
        user.is_email_verified = True
        user.verification_token = None
        user.token_created_at = None
        user.save()

        messages.success(request, "Email успешно подтверждён! Теперь вы можете войти.")
        return redirect("login")


def email_verification_pending(request):
    """Страница с уведомлением о необходимости подтвердить email"""
    return render(request, "users/email_verification_pending.html")


class ManagerRequiredMixin:
    """Mixin для проверки, что пользователь является менеджером"""

    def dispatch(self, request, *args, **kwargs):  # type: ignore[override]
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_manager():
            messages.error(request, "У вас нет доступа к этой странице.")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]


class UserManagementListView(ManagerRequiredMixin, LoginRequiredMixin, View):
    """Список всех пользователей для менеджеров с возможностью блокировки"""

    def get(self, request):
        from django.db.models import Count

        users = User.objects.annotate(
            mailings_count=Count("mailing_owned", distinct=True),
            recipients_count=Count("recipient_owned", distinct=True),
            attempts_count=Count("mailing_owned__attempts", distinct=True),
        ).order_by("-date_joined")

        return render(request, "users/user_management_list.html", {"users": users})


class UserToggleActiveView(ManagerRequiredMixin, LoginRequiredMixin, View):
    """Блокировка/разблокировка пользователя"""

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)

            if user.is_superuser:
                messages.error(request, "Нельзя заблокировать суперпользователя.")
                return redirect("user_management_list")

            if user == request.user:
                messages.error(request, "Нельзя заблокировать самого себя.")
                return redirect("user_management_list")

            if user.is_manager() and not request.user.is_superuser:
                messages.error(request, "Только суперпользователь может блокировать менеджеров.")
                return redirect("user_management_list")

            user.is_active = not user.is_active
            user.save()

            action = "разблокирован" if user.is_active else "заблокирован"
            messages.success(request, f"Пользователь {user.email} успешно {action}.")

        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден.")

        return redirect("user_management_list")
