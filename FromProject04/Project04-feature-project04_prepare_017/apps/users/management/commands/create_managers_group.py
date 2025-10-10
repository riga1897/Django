"""
Management команда для создания группы Managers с необходимыми permissions.
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.mailings.models import Mailing, Message, Recipient
from apps.users.models import User


class Command(BaseCommand):
    """
    Создаёт группу "Managers" и назначает необходимые permissions:
    - Просмотр всех пользователей, получателей, сообщений, рассылок
    - Изменение пользователей (для блокировки через is_active)
    - Изменение рассылок (для отключения через is_active)
    """

    help = 'Создаёт группу "Managers" с необходимыми permissions'

    def handle(self, *args, **options):
        """Основная логика команды"""
        verbosity = options.get("verbosity", 1)

        # Создаём или получаем группу
        group, created = Group.objects.get_or_create(name="Managers")

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Managers" успешно создана.'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Managers" уже существует. Обновляю permissions...'))

        # Получаем ContentType для моделей
        user_ct = ContentType.objects.get_for_model(User)
        recipient_ct = ContentType.objects.get_for_model(Recipient)
        message_ct = ContentType.objects.get_for_model(Message)
        mailing_ct = ContentType.objects.get_for_model(Mailing)

        # Определяем необходимые permissions
        permissions_to_add = [
            # View permissions для всех моделей
            Permission.objects.get(codename="view_user", content_type=user_ct),
            Permission.objects.get(codename="view_recipient", content_type=recipient_ct),
            Permission.objects.get(codename="view_message", content_type=message_ct),
            Permission.objects.get(codename="view_mailing", content_type=mailing_ct),
            # Custom permissions для просмотра всех объектов
            Permission.objects.get(codename="can_view_all_recipients", content_type=recipient_ct),
            Permission.objects.get(codename="can_view_all_messages", content_type=message_ct),
            Permission.objects.get(codename="can_view_all_mailings", content_type=mailing_ct),
            # Change permissions для блокировки пользователей и отключения рассылок
            Permission.objects.get(codename="change_user", content_type=user_ct),
            Permission.objects.get(codename="can_disable_mailing", content_type=mailing_ct),
        ]

        # Назначаем permissions группе
        group.permissions.set(permissions_to_add)

        if verbosity >= 2:
            self.stdout.write("\nДобавлены следующие permissions:")
            for perm in permissions_to_add:
                self.stdout.write(f"  - {perm.codename} ({perm.name})")

        self.stdout.write(
            self.style.SUCCESS(f'\nГруппа "Managers" настроена. Назначено {len(permissions_to_add)} permissions.')
        )
