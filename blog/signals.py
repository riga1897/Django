from typing import Any

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import BlogPost


@receiver(post_delete, sender=BlogPost)
def delete_blogpost_preview_on_delete(sender: type[BlogPost], instance: BlogPost, **kwargs: Any) -> None:
    """
    Удаляет файл изображения через Django storage API при удалении поста блога
    """
    if instance.preview:
        instance.preview.delete(save=False)  # type: ignore[attr-defined]


@receiver(pre_save, sender=BlogPost)
def delete_old_preview_on_update(sender: type[BlogPost], instance: BlogPost, **kwargs: Any) -> None:
    """
    Удаляет старое изображение при замене на новое
    """
    if not instance.pk:
        return

    try:
        old_instance = BlogPost.objects.get(pk=instance.pk)  # type: ignore[attr-defined]
    except BlogPost.DoesNotExist:  # type: ignore[attr-defined]
        return

    if old_instance.preview and old_instance.preview != instance.preview:
        old_instance.preview.delete(save=False)  # type: ignore[attr-defined]
