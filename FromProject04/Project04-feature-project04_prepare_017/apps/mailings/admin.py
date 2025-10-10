from django.contrib import admin

from apps.mailings.models import Attempt, Mailing, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "owner", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email", "full_name", "owner__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "owner", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("subject", "body", "owner__email")
    readonly_fields = ("created_at", "updated_at")


class AttemptInline(admin.TabularInline):
    model = Attempt
    extra = 0
    readonly_fields = ("trigger_type", "status", "server_response", "attempted_at")
    can_delete = False


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("get_message_subject", "owner", "status", "start_datetime", "end_datetime", "is_active")
    list_filter = ("status", "is_active", "created_at")
    search_fields = ("message__subject", "owner__email")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("recipients",)
    inlines = [AttemptInline]

    @admin.display(description="Сообщение")
    def get_message_subject(self, obj):
        return obj.message.subject if obj.message else "-"


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "trigger_type", "status", "attempted_at")
    list_filter = ("trigger_type", "status", "attempted_at")
    search_fields = ("mailing__message__subject", "server_response")
    readonly_fields = ("mailing", "trigger_type", "status", "server_response", "attempted_at")
