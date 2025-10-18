from django.conf import settings
from django.db import models
from django.db.models import CASCADE


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
        on_delete=CASCADE,
        related_name="blog_posts",
        verbose_name="Владелец",
        help_text="Пользователь, создавший запись",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Признак публикации")
    views_count = models.IntegerField(default=0, verbose_name="Количество просмотров")

    class Meta:  # type: ignore[misc]
        verbose_name = "запись блога"
        verbose_name_plural = "записи блога"
        ordering = ["-created_at"]
        permissions = [
            ("can_unpublish_post", "Может отменять публикацию записи блога"),
        ]

    def __str__(self) -> str:
        return self.title
