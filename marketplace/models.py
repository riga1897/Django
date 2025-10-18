from django.conf import settings
from django.db import models
from django.db.models import CASCADE, SET_DEFAULT


def get_deleted_user() -> int:
    """Возвращает ID системного пользователя для удалённых владельцев."""
    from users.models import User

    user, _ = User.objects.get_or_create(
        email="deleted@system.user",
        defaults={
            "username": "deleted@system.user",
            "first_name": "Удалённый",
            "last_name": "Пользователь",
            "is_active": True,
        },
    )
    return user.pk  # type: ignore[return-value]


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Категория", help_text="Введите наименование категории")
    description = models.CharField(
        max_length=150, verbose_name="Описание категории", help_text="Введите описание категории"
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name"]


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name="Наименование", help_text="Введите наименование товара")
    description = models.CharField(
        max_length=150, verbose_name="Описание продукта", help_text="Введите описание товара", null=True, blank=True
    )
    photo = models.ImageField(
        upload_to="products/photos",
        blank=True,
        null=True,
        verbose_name="Фотография",
        help_text="Загрузите изображение товара",
    )
    category = models.ForeignKey(Category, on_delete=CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", help_text="Введите цену товару")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_DEFAULT,
        default=get_deleted_user,  # type: ignore[arg-type]
        related_name="products",
        verbose_name="Владелец",
        help_text="Пользователь, создавший продукт",
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")  # type: ignore[arg-type]
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:  # type: ignore[misc]
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["name"]
        permissions = [
            ("can_unpublish_product", "Может отменять публикацию продукта"),
        ]
