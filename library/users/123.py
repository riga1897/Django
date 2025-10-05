from django.core.management.base import BaseCommand
from .models import CustomUser

class Command(BaseCommand):
    def handle(self, *args, **options):
        user = CustomUser.objects.create(
            username="test_admin",
            email="testadmin@localhost",
            first_name="Admin",
            last_name="Admin",
        )