from django.db import models


class BlogPost(models.Model):
    title: str = models.CharField(max_length=255, verbose_name="Заголовок")
    content: str = models.TextField(verbose_name="Содержимое")
    preview: models.ImageField = models.ImageField(
        upload_to="blogs/previews/",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите изображение для записи блога",
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published: bool = models.BooleanField(default=False, verbose_name="Признак публикации")
    views_count: int = models.IntegerField(default=0, verbose_name="Количество просмотров")

    class Meta:
        verbose_name = "запись блога"
        verbose_name_plural = "записи блога"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
