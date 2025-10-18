from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Загружает тестовые данные (пользователей, категории, товары, посты)"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        self.stdout.write("Загрузка тестовых данных...")  # type: ignore[attr-defined]
        self.stdout.write("  - 2 тестовых пользователя (test1@example.com, test2@example.com)")  # type: ignore[attr-defined]
        self.stdout.write("  - 3 категории (Электроника, Одежда, Книги)")  # type: ignore[attr-defined]
        self.stdout.write("  - 3 товара")  # type: ignore[attr-defined]
        self.stdout.write("  - 2 блог-поста")  # type: ignore[attr-defined]
        self.stdout.write("")  # type: ignore[attr-defined]

        call_command("loaddata", "marketplace/fixtures/data.json")

        self.stdout.write(self.style.SUCCESS("✅ Тестовые данные успешно загружены!"))  # type: ignore[attr-defined]
        self.stdout.write("")  # type: ignore[attr-defined]
        self.stdout.write("Тестовые пользователи:")  # type: ignore[attr-defined]
        self.stdout.write("  • test1@example.com (пароль: test123)")  # type: ignore[attr-defined]
        self.stdout.write("  • test2@example.com (пароль: test123, модератор)")  # type: ignore[attr-defined]
