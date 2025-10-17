from django.contrib import admin

from users.models import User


@admin.register(User)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
    )
    exclude = ("password",)

