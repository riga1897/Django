from django.core.management.base import BaseCommand
from django.db import connection
from marketplace.models import Category, Product


class Command(BaseCommand):
    help = 'Add test students to the database'

    def handle(self, *args, **kwargs):
        # Удаляем существующие записи
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Сбрасываем счетчики инкрементов
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE marketplace_product_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE marketplace_category_id_seq RESTART WITH 1;")