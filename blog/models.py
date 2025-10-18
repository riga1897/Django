from django.conf import settings
from django.db import models
from django.db.models import SET_DEFAULT


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


class BlogPost(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    preview = models.ImageField(
        upload_to="blogs/previews/",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение для записи блога",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_DEFAULT,
        default=get_deleted_user,  # type: ignore[arg-type]
        related_name="blog_posts",
        verbose_name="Владелец",
        help_text="Пользователь, создавший запись",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(default=False, verbose_name="Признак публикации")  # type: ignore[arg-type]
    views_count = models.IntegerField(default=0, verbose_name="Количество просмотров")  # type: ignore[arg-type]

    class Meta:  # type: ignore[misc]
        verbose_name = "запись блога"
        verbose_name_plural = "записи блога"
        ordering = ["-created_at"]
        permissions = [
            ("can_unpublish_post", "Может отменять публикацию записи блога"),
        ]

    def __str__(self) -> str:
        return self.title  # type: ignore[return-value]
