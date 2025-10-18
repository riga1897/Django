from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore[assignment]
    name = "marketplace"

    def ready(self):
        import marketplace.signals  # noqa: F401
