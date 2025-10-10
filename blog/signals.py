from typing import Any

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import BlogPost


@receiver(post_delete, sender=BlogPost)
def delete_blogpost_preview_on_delete(_sender: type[BlogPost], instance: BlogPost, **_kwargs: Any) -> None:
    """
    Удаляет файл изображения через Django storage API при удалении поста блога
    """
    if instance.preview:
        instance.preview.delete(save=False)


@receiver(pre_save, sender=BlogPost)
def delete_old_preview_on_update(_sender: type[BlogPost], instance: BlogPost, **_kwargs: Any) -> None:
    """
    Удаляет старое изображение при замене на новое
    """
    if not instance.pk:
        return

    try:
        old_instance = BlogPost.objects.get(pk=instance.pk)
    except BlogPost.DoesNotExist:
        return

    if old_instance.preview and old_instance.preview != instance.preview:
        old_instance.preview.delete(save=False)
