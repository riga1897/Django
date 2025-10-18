from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load test data from fixture"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        call_command("loaddata", "marketplace/fixtures/data.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded data from fixture"))  # type: ignore[attr-defined]
