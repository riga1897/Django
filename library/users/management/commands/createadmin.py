from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create admin user'
    def handle(self, *args, **options):
        User: type[AbstractBaseUser] = get_user_model()
        user = User.objects.create(
            username="test_admin",
            email="testadmin@localhost",
            first_name="Admin",
            last_name="Admin",
        )

        user.is_staff = True
        user.is_superuser = True

        user.set_password("1234")

        user.save()

        self.stdout.write(self.style.SUCCESS(f"Администратор успешно создан"))