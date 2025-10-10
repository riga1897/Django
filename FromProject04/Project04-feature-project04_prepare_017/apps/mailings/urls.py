from django.urls import path

from apps.mailings.views import (
    AttemptListView,
    MailingCreateView,
    MailingDeleteView,
    MailingListView,
    MailingReportsView,
    MailingToggleActiveView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageListView,
    MessageUpdateView,
    RecipientCreateView,
    RecipientDeleteView,
    RecipientListView,
    RecipientUpdateView,
    SendMailingView,
)

urlpatterns = [
    # Получатели (Recipients)
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipients/<int:pk>/edit/", RecipientUpdateView.as_view(), name="recipient_edit"),
    path("recipients/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_delete"),
    # Сообщения (Messages)
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_edit"),
    path("messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    # Рассылки (Mailings)
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing_edit"),
    path("mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailings/<int:pk>/send/", SendMailingView.as_view(), name="mailing_send"),
    path("mailings/<int:pk>/toggle-active/", MailingToggleActiveView.as_view(), name="mailing_toggle_active"),
    path("reports/", MailingReportsView.as_view(), name="mailing_reports"),
    # Попытки рассылок
    path("attempts/", AttemptListView.as_view(), name="attempt_list"),
]
