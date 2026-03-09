from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Create a superuser with email admin@example.com"

    def handle(self, *args, **options):
        email = "admin@example.com"
        password = "admin123"

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User with email {email} already exists"))
            return

        User.objects.create_superuser(email=email, password=password, phone="+1234567890", country="US")

        self.stdout.write(self.style.SUCCESS("Superuser created successfully!"))
        self.stdout.write(self.style.SUCCESS(f"Email: {email}"))
        self.stdout.write(self.style.SUCCESS(f"Password: {password}"))
