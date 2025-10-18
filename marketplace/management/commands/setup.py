from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Инициализирует чистую платформу: системный пользователь, группы прав, суперпользователь"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        self.stdout.write(self.style.WARNING("Инициализация платформы..."))  # type: ignore[attr-defined]

        # Шаг 1: Полная очистка базы данных
        self.stdout.write(self.style.WARNING("\n1. Очистка базы данных..."))  # type: ignore[attr-defined]
        call_command("del_all")

        # Шаг 2: Загрузка системного пользователя
        self.stdout.write(self.style.WARNING("\n2. Создание системного пользователя..."))  # type: ignore[attr-defined]
        call_command("loaddata", "users/fixtures/system_user.json")
        self.stdout.write(self.style.SUCCESS("   Системный пользователь deleted@system.user создан"))  # type: ignore[attr-defined]

        # Шаг 3: Загрузка групп и прав
        self.stdout.write(self.style.WARNING("\n3. Создание групп прав доступа..."))  # type: ignore[attr-defined]
        call_command("loaddata", "marketplace/fixtures/groups_and_permissions.json")
        self.stdout.write(self.style.SUCCESS("   Группы 'Модератор продуктов' и 'Контент-менеджер' созданы"))  # type: ignore[attr-defined]

        # Шаг 4: Создание суперпользователя
        self.stdout.write(self.style.WARNING("\n4. Создание суперпользователя..."))  # type: ignore[attr-defined]
        email = "admin@example.com"
        password = "admin123"

        if not User.objects.filter(email=email).exists():  # type: ignore[attr-defined]
            User.objects.create_superuser(  # type: ignore[attr-defined]
                email=email, password=password, phone="+1234567890", country="US"
            )
            self.stdout.write(self.style.SUCCESS("   Суперпользователь создан:"))  # type: ignore[attr-defined]
            self.stdout.write(self.style.SUCCESS(f"   Email: {email}"))  # type: ignore[attr-defined]
            self.stdout.write(self.style.SUCCESS(f"   Пароль: {password}"))  # type: ignore[attr-defined]
        else:
            self.stdout.write(self.style.WARNING(f"   Пользователь {email} уже существует"))  # type: ignore[attr-defined]

        # Финальное сообщение
        self.stdout.write(self.style.SUCCESS("\n✅ Платформа готова к работе!"))  # type: ignore[attr-defined]
        self.stdout.write(self.style.SUCCESS("Вы можете войти как администратор:"))  # type: ignore[attr-defined]
        self.stdout.write(self.style.SUCCESS(f"  Email: {email}"))  # type: ignore[attr-defined]
        self.stdout.write(self.style.SUCCESS(f"  Пароль: {password}"))  # type: ignore[attr-defined]
