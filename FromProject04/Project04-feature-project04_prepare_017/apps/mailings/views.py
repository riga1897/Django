import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.mailings.forms import MailingForm, MailingUpdateForm, MessageForm, RecipientForm
from apps.mailings.models import Attempt, Mailing, Message, Recipient
from apps.users.views import EmailVerifiedRequiredMixin, ManagerRequiredMixin

logger = logging.getLogger("apps.mailings")


def home(request):
    """Главная страница с общей статистикой"""
    # Проверяем статус scheduler
    from apps.mailings.apps import _scheduler_started

    # Получаем время последнего запуска планировщика
    scheduler_last_run = cache.get("scheduler_last_run")

    if not request.user.is_authenticated:
        # Для неавторизованных пользователей показываем нули
        stats = {
            "total_mailings": 0,
            "active_mailings": 0,
            "unique_recipients": 0,
            "scheduler_running": _scheduler_started,
            "scheduler_last_run": scheduler_last_run,
        }
        return render(request, "home.html", stats)

    # Проверка подтверждения email
    if not request.user.is_email_verified:
        return redirect("email_verification_pending")

    # Для авторизованных пользователей используем пользователь-специфичный кеш
    user_id = request.user.id
    cache_key_mailings = f"user_{user_id}_total_mailings"
    cache_key_active = f"user_{user_id}_active_mailings"
    cache_key_recipients = f"user_{user_id}_unique_recipients"

    total_mailings = cache.get(cache_key_mailings)
    active_mailings = cache.get(cache_key_active)
    unique_recipients = cache.get(cache_key_recipients)

    if total_mailings is None:
        total_mailings = Mailing.objects.filter(owner=request.user, is_active=True).count()
        cache.set(cache_key_mailings, total_mailings, 300)

    if active_mailings is None:
        active_mailings = Mailing.objects.filter(
            owner=request.user, status=Mailing.STATUS_RUNNING, is_active=True
        ).count()
        cache.set(cache_key_active, active_mailings, 300)

    if unique_recipients is None:
        unique_recipients = Recipient.objects.filter(owner=request.user, is_active=True).distinct().count()
        cache.set(cache_key_recipients, unique_recipients, 300)

    stats = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
        "scheduler_running": _scheduler_started,
        "scheduler_last_run": scheduler_last_run,
    }

    return render(request, "home.html", stats)


# CRUD для Recipient
class RecipientListView(EmailVerifiedRequiredMixin, LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailings/recipient_list.html"
    context_object_name = "recipients"
    paginate_by = 10

    def get_queryset(self):
        queryset = Recipient.objects.filter(is_active=True)
        # Менеджеры видят всех получателей
        if not self.request.user.is_manager():  # type: ignore[union-attr]
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class RecipientCreateView(EmailVerifiedRequiredMixin, LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = "mailings/recipient_form.html"
    form_class = RecipientForm
    success_url = reverse_lazy("recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(EmailVerifiedRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Recipient
    template_name = "mailings/recipient_form.html"
    form_class = RecipientForm
    success_url = reverse_lazy("recipient_list")

    def get_queryset(self):
        queryset = Recipient.objects.filter(is_active=True)
        # Менеджеры могут просматривать всех получателей
        if not self.request.user.is_manager():  # type: ignore[union-attr]
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Read-only режим для менеджеров, просматривающих чужие данные
        context["read_only_mode"] = self.request.user.is_manager() and self.object.owner != self.request.user  # type: ignore[union-attr]
        return context

    def form_valid(self, form):
        # Запретить менеджерам редактировать чужие данные (защита от client-side изменений)
        if self.request.user.is_manager() and self.object.owner != self.request.user:  # type: ignore[union-attr]
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("Менеджеры могут только просматривать чужие данные.")
        return super().form_valid(form)


class RecipientDeleteView(EmailVerifiedRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailings/recipient_confirm_delete.html"
    success_url = reverse_lazy("recipient_list")

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user, is_active=True)


# CRUD для Message
class MessageListView(EmailVerifiedRequiredMixin, LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = "messages_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = Message.objects.filter(is_active=True)
        # Менеджеры видят все сообщения
        if not self.request.user.is_manager():  # type: ignore[union-attr]
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class MessageCreateView(EmailVerifiedRequiredMixin, LoginRequiredMixin, CreateView):
    model = Message
    template_name = "mailings/message_form.html"
    form_class = MessageForm
    success_url = reverse_lazy("message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(EmailVerifiedRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Message
    template_name = "mailings/message_form.html"
    form_class = MessageForm
    success_url = reverse_lazy("message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user, is_active=True)


class MessageDeleteView(EmailVerifiedRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailings/message_confirm_delete.html"
    success_url = reverse_lazy("message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user, is_active=True)


# CRUD для Mailing
class MailingListView(EmailVerifiedRequiredMixin, LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"
    paginate_by = 10

    def get_queryset(self):
        queryset = Mailing.objects.all()
        # Менеджеры видят все рассылки
        if not self.request.user.is_manager():  # type: ignore[union-attr]
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем error_mailing_id, error_text и error_details если они были установлены
        if hasattr(self.request, "error_mailing_id"):
            context["error_mailing_id"] = self.request.error_mailing_id
        if hasattr(self.request, "error_text"):
            context["error_text"] = self.request.error_text
        if hasattr(self.request, "error_details"):
            context["error_details"] = self.request.error_details
        return context


class MailingCreateView(EmailVerifiedRequiredMixin, LoginRequiredMixin, CreateView):
    model = Mailing
    template_name = "mailings/mailing_form.html"
    form_class = MailingForm
    success_url = reverse_lazy("mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(EmailVerifiedRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Mailing
    template_name = "mailings/mailing_form.html"
    form_class = MailingUpdateForm
    success_url = reverse_lazy("mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Для менеджеров, просматривающих чужие данные, передаем владельца
        # чтобы форма показывала правильные message/recipients
        if hasattr(self, "object") and self.request.user.is_manager() and self.object.owner != self.request.user:  # type: ignore[union-attr]
            kwargs["user"] = self.object.owner
        else:
            kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        queryset = Mailing.objects.all()
        # Менеджеры могут просматривать все рассылки
        if not self.request.user.is_manager():  # type: ignore[union-attr]
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Read-only режим для менеджеров, просматривающих чужие данные
        context["read_only_mode"] = self.request.user.is_manager() and self.object.owner != self.request.user  # type: ignore[union-attr]
        return context

    def form_valid(self, form):
        # Запретить менеджерам редактировать чужие данные (защита от client-side изменений)
        if self.request.user.is_manager() and self.object.owner != self.request.user:  # type: ignore[union-attr]
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("Менеджеры могут только просматривать чужие данные.")
        return super().form_valid(form)


class MailingDeleteView(EmailVerifiedRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing_list")

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class AttemptListView(EmailVerifiedRequiredMixin, LoginRequiredMixin, ListView):
    """Список всех попыток отправки"""

    model = Attempt
    template_name = "mailings/attempt_list.html"
    context_object_name = "attempts"
    paginate_by = 20

    def get_queryset(self):
        """Получаем попытки для рассылок текущего пользователя или все для менеджеров"""
        queryset = Attempt.objects.select_related("mailing", "mailing__message", "mailing__owner", "recipient")
        # Менеджеры видят все попытки
        if not self.request.user.is_manager():  # type: ignore[union-attr]
            queryset = queryset.filter(mailing__owner=self.request.user)
        return queryset.order_by("-attempted_at")


class MailingReportsView(EmailVerifiedRequiredMixin, LoginRequiredMixin, ListView):
    """Страница с отчетами по рассылкам пользователя"""

    model = Mailing
    template_name = "mailings/mailing_reports.html"
    context_object_name = "reports"
    paginate_by = 20

    def get_queryset(self):
        """Получаем рассылки с агрегированной статистикой для текущего пользователя или все для менеджеров"""
        from django.db.models import Count, Prefetch, Q

        failed_attempts_prefetch = Prefetch(
            "attempts",
            queryset=Attempt.objects.filter(status=Attempt.STATUS_FAILURE)
            .select_related("recipient")
            .order_by("-attempted_at")[:10],
            to_attr="failed_attempt_list",
        )

        queryset = Mailing.objects.all()
        # Менеджеры видят все отчеты
        if not self.request.user.is_manager():  # type: ignore[union-attr]
            queryset = queryset.filter(owner=self.request.user)

        return (
            queryset.select_related("message", "owner")
            .prefetch_related("recipients", failed_attempts_prefetch)
            .annotate(
                total_recipients=Count("recipients", distinct=True),
                successful_attempts=Count("attempts", filter=Q(attempts__status=Attempt.STATUS_SUCCESS)),
                failed_attempts=Count("attempts", filter=Q(attempts__status=Attempt.STATUS_FAILURE)),
            )
            .order_by("-created_at")
        )


class SendMailingView(EmailVerifiedRequiredMixin, LoginRequiredMixin, View):
    """
    View для отправки рассылки из веб-интерфейса.

    Логика:
    1. Проверяет права доступа (пользователь владелец)
    2. Проверяет статус рассылки (должен быть Created)
    3. Отправляет email всем получателям
    4. Создаёт Attempt записи для каждой попытки
    5. Меняет статус на Completed
    6. Перенаправляет на список рассылок с сообщением
    """

    def _render_list_with_error(self, request, mailing_id, error_text, error_details=None):
        """Рендерит список рассылок с отображением ошибки для конкретной рассылки"""
        list_view = MailingListView.as_view()
        request.error_mailing_id = mailing_id
        request.error_text = error_text
        request.error_details = error_details if error_details else []
        return list_view(request)

    def _validate_mailing_for_send(self, mailing, request):
        """Проверяет, можно ли отправить рассылку. Возвращает (is_valid, error_response)"""
        if not mailing.is_active:
            error_text = "Невозможно отправить отключенную рассылку. Попросите менеджера включить её."
            return False, self._render_list_with_error(request, mailing.pk, error_text)

        if mailing.status == Mailing.STATUS_COMPLETED:
            error_text = f"Рассылка уже завершена (статус: {mailing.get_status_display()})."
            return False, self._render_list_with_error(request, mailing.pk, error_text)

        if mailing.successfully_sent:
            error_text = "Рассылка уже успешно отправлена."
            return False, self._render_list_with_error(request, mailing.pk, error_text)

        recipients = mailing.recipients.all()
        if not recipients.exists():
            error_text = "Рассылка не имеет получателей."
            mailing.status = Mailing.STATUS_COMPLETED
            mailing.save(update_fields=["status"])
            return False, self._render_list_with_error(request, mailing.pk, error_text)

        return True, None

    def _send_emails_to_recipients(self, mailing, recipients, request):
        """Отправляет email всем получателям. Возвращает (success_count, failure_count)"""
        success_count = 0
        failure_count = 0

        for recipient in recipients:
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                Attempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    run_number=mailing.current_run,
                    trigger_type=Attempt.TRIGGER_MANUAL,
                    status=Attempt.STATUS_SUCCESS,
                    server_response="Email отправлен успешно",
                )
                success_count += 1
            except Exception as e:
                Attempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    run_number=mailing.current_run,
                    trigger_type=Attempt.TRIGGER_MANUAL,
                    status=Attempt.STATUS_FAILURE,
                    server_response=str(e),
                )
                failure_count += 1
                logger.error(
                    f"Ошибка отправки рассылки #{mailing.pk} получателю {recipient.email}: {e}", exc_info=True
                )

        return success_count, failure_count

    def _update_mailing_status_after_send(self, mailing, success_count, failure_count):
        """Обновляет статус рассылки после отправки"""
        if failure_count == 0:
            # Полный успех - переводим сразу в Completed
            mailing.successfully_sent = True
            mailing.status = Mailing.STATUS_COMPLETED
            mailing.save(update_fields=["successfully_sent", "status"])
            logger.info(f"Рассылка #{mailing.pk} успешно отправлена всем получателям. Успешно: {success_count}")
        else:
            # Частичная неудача - статус остается Running для повторной попытки
            logger.info(
                f"Рассылка #{mailing.pk} завершена с ошибками. Успешно: {success_count}, Ошибки: {failure_count}"
            )

    def post(self, request, pk):
        """Отправка рассылки"""
        # Получаем рассылку и проверяем права
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

        # Валидация рассылки
        is_valid, error_response = self._validate_mailing_for_send(mailing, request)
        if not is_valid:
            return error_response

        # Меняем статус на Running (если еще не Running)
        recipients = mailing.recipients.all()
        if mailing.status == Mailing.STATUS_CREATED:
            mailing.status = Mailing.STATUS_RUNNING
            mailing.save(update_fields=["status"])

        logger.info(
            f"Начало отправки рассылки #{mailing.pk}: "
            f"'{mailing.message.subject}' для {recipients.count()} получателей "  # type: ignore[attr-defined]
            f"(пользователь {request.user.email})"
        )

        # Отправляем email всем получателям
        success_count, failure_count = self._send_emails_to_recipients(mailing, recipients, request)

        # Обновляем статус рассылки
        self._update_mailing_status_after_send(mailing, success_count, failure_count)

        # Сообщение пользователю
        if failure_count == 0:
            messages.success(request, f"Рассылка отправлена успешно! Получателей: {success_count}")
            return redirect("mailing_list")
        else:
            # Собираем детальные ошибки для отображения
            failed_attempts = (
                Attempt.objects.filter(mailing=mailing, status=Attempt.STATUS_FAILURE)
                .select_related("recipient")
                .order_by("-attempted_at")[:10]
            )

            error_details = []
            for attempt in failed_attempts:
                # Обрезаем текст ошибки до 150 символов
                error_msg = attempt.server_response or "Неизвестная ошибка"
                if len(error_msg) > 150:
                    error_msg = error_msg[:150] + "..."

                recipient_email = attempt.recipient.email if attempt.recipient else "Неизвестный получатель"  # type: ignore[attr-defined]
                error_details.append(f"Получатель {recipient_email}: {error_msg}")

            error_text = f"Рассылка завершена. Успешно: {success_count}, Ошибки: {failure_count}"
            return self._render_list_with_error(request, pk, error_text, error_details)


class MailingToggleActiveView(ManagerRequiredMixin, LoginRequiredMixin, View):
    """Отключение/включение рассылки менеджером"""

    def post(self, request, pk):
        from django.http import JsonResponse

        try:
            mailing = Mailing.objects.select_related("owner").get(pk=pk)

            if mailing.owner.is_manager() and not request.user.is_superuser:  # type: ignore[attr-defined]
                error_msg = "Только суперпользователь может управлять рассылками менеджеров."
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"success": False, "error": error_msg}, status=403)
                messages.error(request, error_msg)
                return redirect("mailing_list")

            if not mailing.owner.is_active:  # type: ignore[attr-defined]
                error_msg = "Нельзя управлять рассылками заблокированного пользователя."
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"success": False, "error": error_msg}, status=403)
                messages.error(request, error_msg)
                return redirect("mailing_list")

            mailing.is_active = not mailing.is_active
            mailing.save(update_fields=["is_active"])

            action = "включена" if mailing.is_active else "отключена"
            success_msg = f'Рассылка "{mailing.message.subject}" успешно {action}.'  # type: ignore[attr-defined]

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": True, "is_active": mailing.is_active, "message": success_msg})

            messages.success(request, success_msg)

        except Mailing.DoesNotExist:
            error_msg = "Рассылка не найдена."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": error_msg}, status=404)
            messages.error(request, error_msg)

        return redirect("mailing_list")
