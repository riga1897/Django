from typing import Any

from django.core.management.base import BaseCommand
from django.db import connection

from blog.models import BlogPost
from marketplace.models import Category, Product
from users.models import User


class Command(BaseCommand):
    help = "Удаляет все данные из базы и сбрасывает все счетчики"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        self.stdout.write(self.style.WARNING("Удаление всех данных из базы..."))  # type: ignore[attr-defined]

        # Удаляем все записи (сначала контент, потом владельцев, потом категории)
        deleted_posts = BlogPost.objects.all().delete()  # type: ignore[attr-defined]
        deleted_products = Product.objects.all().delete()  # type: ignore[attr-defined]
        deleted_users = User.objects.all().delete()  # type: ignore[attr-defined]
        deleted_categories = Category.objects.all().delete()  # type: ignore[attr-defined]

        # Сбрасываем счетчики инкрементов
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE users_user_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE blog_blogpost_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE marketplace_product_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE marketplace_category_id_seq RESTART WITH 1;")

        self.stdout.write(self.style.SUCCESS(f"Удалено пользователей: {deleted_users[0]}"))  # type: ignore[attr-defined]
        self.stdout.write(self.style.SUCCESS(f"Удалено блог-постов: {deleted_posts[0]}"))  # type: ignore[attr-defined]
        self.stdout.write(self.style.SUCCESS(f"Удалено товаров: {deleted_products[0]}"))  # type: ignore[attr-defined]
        self.stdout.write(self.style.SUCCESS(f"Удалено категорий: {deleted_categories[0]}"))  # type: ignore[attr-defined]
        self.stdout.write(self.style.SUCCESS("Все счетчики сброшены!"))  # type: ignore[attr-defined]
