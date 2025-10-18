from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Загружает все тестовые данные (пользователи, группы, категории, товары, посты)"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        self.stdout.write("Загрузка тестовых данных...")  # type: ignore[attr-defined]

        # Загружаем фикстуры в правильном порядке
        self.stdout.write("1. Загрузка системного пользователя...")  # type: ignore[attr-defined]
        call_command("loaddata", "users/fixtures/system_user.json")

        self.stdout.write("2. Загрузка групп прав доступа...")  # type: ignore[attr-defined]
        call_command("loaddata", "marketplace/fixtures/groups_and_permissions.json")

        self.stdout.write("3. Загрузка категорий, товаров и блог-постов...")  # type: ignore[attr-defined]
        call_command("loaddata", "marketplace/fixtures/data.json")

        self.stdout.write(self.style.SUCCESS("\n✅ Все тестовые данные успешно загружены!"))  # type: ignore[attr-defined]
