"""
Модели для приложения mailings.

Содержит модели для управления рассылками, сообщениями и получателями.
"""

from django.db import models

from apps.core.models import OwnedModel


class Recipient(OwnedModel):
    """
    Модель получателя рассылки.

    Атрибуты:
        email: Email получателя
        full_name: Полное имя получателя
        comment: Комментарий о получателе
        owner: Владелец записи (FK к User)
    """

    email: models.EmailField = models.EmailField(verbose_name="Email", help_text="Email адрес получателя")

    full_name: models.CharField = models.CharField(
        max_length=255, verbose_name="Полное имя", help_text="ФИО получателя"
    )

    comment: models.TextField = models.TextField(
        verbose_name="Комментарий", blank=True, null=True, help_text="Дополнительная информация о получателе"
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["full_name"]
        unique_together = [["email", "owner"]]
        permissions = [
            ("can_view_all_recipients", "Может просматривать всех получателей"),
        ]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Message(OwnedModel):
    """
    Модель сообщения для рассылки.

    Атрибуты:
        subject: Тема письма
        body: Текст письма
        owner: Владелец записи (FK к User)
    """

    subject: models.CharField = models.CharField(
        max_length=255, verbose_name="Тема письма", help_text="Тема email сообщения"
    )

    body: models.TextField = models.TextField(verbose_name="Текст письма", help_text="Содержание email сообщения")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]
        permissions = [
            ("can_view_all_messages", "Может просматривать все сообщения"),
        ]

    def __str__(self):
        return self.subject


class Mailing(OwnedModel):
    """
    Модель рассылки.

    Атрибуты:
        start_datetime: Дата и время начала рассылки
        end_datetime: Дата и время окончания рассылки
        status: Статус рассылки (Created/Running/Completed)
        message: Сообщение для рассылки (FK к Message)
        recipients: Получатели рассылки (M2M к Recipient)
        owner: Владелец записи (FK к User)
        successfully_sent: Флаг успешной отправки
        is_active: Флаг активности (менеджеры могут отключать)
        current_run: Номер текущего запуска (увеличивается при повторной отправке)
    """

    STATUS_CREATED = "created"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_RUNNING, "Запущена"),
        (STATUS_COMPLETED, "Завершена"),
    ]

    start_datetime: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата и время начала", help_text="Когда начать рассылку"
    )

    end_datetime: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата и время окончания", help_text="Когда завершить рассылку"
    )

    status: models.CharField = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус",
        help_text="Текущий статус рассылки",
    )

    message: models.ForeignKey = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
        help_text="Сообщение для отправки",
    )

    recipients: models.ManyToManyField = models.ManyToManyField(
        Recipient, related_name="mailings", verbose_name="Получатели", help_text="Получатели рассылки"
    )

    successfully_sent: models.BooleanField = models.BooleanField(
        default=False, verbose_name="Успешно отправлена", help_text="Флаг успешной отправки рассылки всем получателям"
    )

    is_active: models.BooleanField = models.BooleanField(
        default=True, verbose_name="Активна", help_text="Флаг активности рассылки (менеджеры могут отключать)"
    )

    current_run: models.PositiveIntegerField = models.PositiveIntegerField(
        default=1,
        verbose_name="Текущий запуск",
        help_text="Номер текущего запуска рассылки (увеличивается при повторной отправке)",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]
        permissions = [
            ("can_view_all_mailings", "Может просматривать все рассылки"),
            ("can_disable_mailing", "Может отключать рассылки"),
        ]

    def __str__(self):
        return f"Рассылка: {self.message.subject} ({self.get_status_display()})"  # type: ignore[attr-defined]


class Attempt(models.Model):
    """
    Модель попытки отправки рассылки.

    Атрибуты:
        mailing: Рассылка (FK к Mailing)
        recipient: Получатель (FK к Recipient)
        run_number: Номер запуска рассылки (для отслеживания повторных отправок)
        trigger_type: Способ запуска рассылки
        status: Статус попытки (Success/Failure)
        server_response: Ответ сервера
        attempted_at: Дата и время попытки
    """

    STATUS_SUCCESS = "success"
    STATUS_FAILURE = "failure"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILURE, "Ошибка"),
    ]

    TRIGGER_MANUAL = "manual"
    TRIGGER_SCHEDULED = "scheduled"
    TRIGGER_COMMAND = "command"

    TRIGGER_CHOICES = [
        (TRIGGER_MANUAL, "Вручную (веб-интерфейс)"),
        (TRIGGER_SCHEDULED, "Автоматически (по расписанию)"),
        (TRIGGER_COMMAND, "Команда (management command)"),
    ]

    mailing: models.ForeignKey = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
        help_text="К какой рассылке относится попытка",
    )

    recipient: models.ForeignKey = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Получатель",
        help_text="Кому отправлялось письмо",
        null=True,
        blank=True,
    )

    run_number: models.PositiveIntegerField = models.PositiveIntegerField(
        default=1,
        verbose_name="Номер запуска",
        help_text="Номер запуска рассылки (для отслеживания повторных отправок)",
    )

    trigger_type: models.CharField = models.CharField(
        max_length=20,
        choices=TRIGGER_CHOICES,
        default=TRIGGER_MANUAL,
        verbose_name="Способ запуска",
        help_text="Как была запущена рассылка",
    )

    status: models.CharField = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус", help_text="Результат попытки отправки"
    )

    server_response: models.TextField = models.TextField(
        verbose_name="Ответ сервера", blank=True, null=True, help_text="Технический ответ почтового сервера"
    )

    attempted_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата попытки", help_text="Когда была выполнена попытка отправки"
    )

    class Meta:
        verbose_name = "Попытка отправки"
        verbose_name_plural = "Попытки отправки"
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"Попытка {self.get_status_display()} - {self.attempted_at}"  # type: ignore[attr-defined]
