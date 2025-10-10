from django import forms

from apps.mailings.models import Mailing, Message, Recipient


class RecipientForm(forms.ModelForm):
    """Форма для создания/редактирования получателя"""

    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comment"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Иван Иванов"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Дополнительная информация"}
            ),
        }
        labels = {
            "email": "Email",
            "full_name": "Полное имя",
            "comment": "Комментарий",
        }


class MessageForm(forms.ModelForm):
    """Форма для создания/редактирования сообщения"""

    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Тема сообщения"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 10, "placeholder": "Текст сообщения"}),
        }
        labels = {
            "subject": "Тема",
            "body": "Текст",
        }


class MailingForm(forms.ModelForm):
    """Форма для создания/редактирования рассылки"""

    class Meta:
        model = Mailing
        fields = ["start_datetime", "end_datetime", "message", "recipients"]
        widgets = {
            "start_datetime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "message": forms.Select(attrs={"class": "form-select"}),
            "recipients": forms.SelectMultiple(attrs={"class": "form-select"}),
        }
        labels = {
            "start_datetime": "Дата и время начала",
            "end_datetime": "Дата и время окончания",
            "message": "Сообщение",
            "recipients": "Получатели",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Фильтруем доступные сообщения и получателей по владельцу
        if user:
            self.fields["message"].queryset = Message.objects.filter(owner=user, is_active=True)  # type: ignore[attr-defined]
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user, is_active=True)  # type: ignore[attr-defined]

        # Устанавливаем input_formats для datetime полей
        self.fields["start_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]  # type: ignore[attr-defined]
        self.fields["end_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]  # type: ignore[attr-defined]


class MailingUpdateForm(MailingForm):
    """Форма для редактирования рассылки (с возможностью изменения статуса)"""

    class Meta(MailingForm.Meta):
        fields = ["start_datetime", "end_datetime", "status", "message", "recipients"]
        widgets = {
            **MailingForm.Meta.widgets,
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            **MailingForm.Meta.labels,
            "status": "Статус",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Сохраняем исходный статус для отслеживания изменений
        if self.instance and self.instance.pk:
            self._original_status = self.instance.status
        else:
            self._original_status = None

    def save(self, commit=True):
        """
        Переопределяем save для:
        1. Сброса successfully_sent и увеличения current_run при изменении статуса на 'created'
        2. Создания записей Attempt при ручном изменении статуса на 'running'/'completed'
        """
        from django.db.models import F

        from apps.mailings.models import Attempt

        instance = super().save(commit=False)
        status_changed = self._original_status and self._original_status != instance.status

        # Если статус изменен на "Создана" - сбрасываем флаг и увеличиваем current_run
        if status_changed and instance.status == "created":
            instance.successfully_sent = False
            # Увеличиваем номер запуска для повторной отправки
            instance.current_run = F("current_run") + 1

        if commit:
            instance.save()
            # Если использовали F() expression, нужно обновить instance
            if status_changed and instance.status == "created":
                instance.refresh_from_db()

            # Если статус изменен вручную на "Running" или "Completed" - создаем Attempt
            if status_changed and instance.status in ["running", "completed"]:
                # Создаем записи для всех получателей рассылки
                for recipient in instance.recipients.all():
                    Attempt.objects.create(
                        mailing=instance,
                        recipient=recipient,
                        run_number=instance.current_run,
                        trigger_type=Attempt.TRIGGER_MANUAL,
                        status=Attempt.STATUS_SUCCESS,
                        server_response=f"Статус изменен вручную: {self._original_status} → {instance.status}",
                    )

        return instance
