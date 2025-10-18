from typing import Any

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Загрузка фикстур для начальной настройки проекта"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--users",
            action="store_true",
            help="Загрузить системного пользователя",
        )
        parser.add_argument(
            "--groups",
            action="store_true",
            help="Загрузить группы модераторов и разрешения",
        )
        parser.add_argument(
            "--data",
            action="store_true",
            help="Загрузить данные (категории, товары, блог-посты)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Если не указаны флаги - загружаем всё
        load_all = not any([options["users"], options["groups"], options["data"]])

        if options["users"] or load_all:
            self._load_system_user()

        if options["groups"] or load_all:
            self._load_groups()

        if options["data"] or load_all:
            self._load_data()

        self.stdout.write(self.style.SUCCESS("\n✅ Настройка завершена успешно!"))  # type: ignore[attr-defined]

    def _load_system_user(self) -> None:
        """Загрузка системного пользователя"""
        system_email = "deleted@system.user"

        if User.objects.filter(email=system_email).exists():  # type: ignore[attr-defined]
            self.stdout.write(
                self.style.WARNING(  # type: ignore[attr-defined]
                    f"⏭️  Системный пользователь '{system_email}' уже существует"
                )
            )
            return

        self.stdout.write("📦 Загрузка системного пользователя...")
        call_command("loaddata", "users/fixtures/system_user.json", verbosity=0)
        self.stdout.write(
            self.style.SUCCESS(f"✅ Системный пользователь '{system_email}' загружен")  # type: ignore[attr-defined]
        )

    def _load_groups(self) -> None:
        """Загрузка групп модераторов и разрешений"""
        required_groups = ["Модератор продуктов", "Контент-менеджер"]
        existing_groups = Group.objects.filter(name__in=required_groups).values_list(  # type: ignore[attr-defined]
            "name", flat=True
        )

        if set(existing_groups) == set(required_groups):
            self.stdout.write(self.style.WARNING("⏭️  Группы модераторов уже существуют"))  # type: ignore[attr-defined]
            return

        self.stdout.write("📦 Загрузка групп модераторов и разрешений...")
        call_command("loaddata", "marketplace/fixtures/groups_and_permissions.json", verbosity=0)
        self.stdout.write(
            self.style.SUCCESS("✅ Группы модераторов и разрешения загружены")  # type: ignore[attr-defined]
        )

    def _load_data(self) -> None:
        """Загрузка данных (категории, товары, блог-посты)"""
        from blog.models import BlogPost
        from marketplace.models import Category, Product

        has_data = (
            Category.objects.exists()  # type: ignore[attr-defined]
            or Product.objects.exists()  # type: ignore[attr-defined]
            or BlogPost.objects.exists()  # type: ignore[attr-defined]
        )

        if has_data:
            self.stdout.write(
                self.style.WARNING("⚠️  База данных уже содержит категории/товары/посты")  # type: ignore[attr-defined]
            )
            response = input("   Загрузить данные в любом случае? Это добавит новые записи (y/N): ")
            if response.lower() != "y":
                self.stdout.write(self.style.WARNING("⏭️  Загрузка данных пропущена"))  # type: ignore[attr-defined]
                return

        self.stdout.write("📦 Загрузка данных (категории, товары, блог-посты)...")
        call_command("loaddata", "marketplace/fixtures/data.json", verbosity=0)
        self.stdout.write(
            self.style.SUCCESS("✅ Данные (категории, товары, блог-посты) загружены")  # type: ignore[attr-defined]
        )
