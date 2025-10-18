from typing import Any

from django.core.management.base import BaseCommand
from django.db import connection

from marketplace.models import Category, Product


class Command(BaseCommand):
    help = "Add test students to the database"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        # Удаляем существующие записи
        Product.objects.all().delete()  # type: ignore[attr-defined]
        Category.objects.all().delete()  # type: ignore[attr-defined]

        # Сбрасываем счетчики инкрементов
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE marketplace_product_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE marketplace_category_id_seq RESTART WITH 1;")

        category, _ = Category.objects.get_or_create(  # type: ignore[attr-defined]
            name="Смартфоны",
            description=(
                "Смартфоны, как средство не только коммуникации,"
                " но и получения дополнительных функций для удобства жизни",
            ),
        )

        products = [
            {
                "name": "Iphone 15",
                "description": "512GB, Gray space",
                "photo": "products/photos/iphone15gray.jpg",
                "price": "21000.00",
                "category": category,
            }
        ]

        category, _ = Category.objects.get_or_create(  # type: ignore[attr-defined]
            name="Телевизоры",
            description=(
                "Современный телевизор, который позволяет наслаждаться просмотром,"
                " станет вашим другом и помощником",
            ),
        )

        products += [
            {
                "name": '55" QLED 4K',
                "description": "Фоновая подсветка",
                "photo": "products/photos/55QLed.jpg",
                "price": "123000.00",
                "category": category,
            }
        ]

        for product_data in products:
            product_obj, created = Product.objects.get_or_create(**product_data)  # type: ignore[attr-defined,arg-type]
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added product: {product_obj.name}"))  # type: ignore[attr-defined]
            else:
                self.stdout.write(self.style.WARNING(f"Product already exists: {product_obj.name}"))  # type: ignore[attr-defined]
