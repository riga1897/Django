
from django.core.management.base import BaseCommand
from django.db import connection

from students.models import Student, Group


class DelCommand(BaseCommand):
    help = 'Add test students to the database'

    def handle(self, *args, **kwargs):
        # Удаляем существующие записи
        Student.objects.all().delete()
        Group.objects.all().delete()

        # Сбрасываем счетчики инкрементов
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE students_student_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE students_group_id_seq RESTART WITH 1;")