from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Product


@receiver(post_delete, sender=Product)
def delete_product_photo_on_delete(sender, instance, **kwargs):
    """
    Удаляет файл изображения через Django storage API при удалении товара
    """
    if instance.photo:
        instance.photo.delete(save=False)


@receiver(pre_save, sender=Product)
def delete_old_photo_on_update(sender, instance, **kwargs):
    """
    Удаляет старое изображение при замене на новое
    """
    if not instance.pk:
        return

    try:
        old_instance = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return

    if old_instance.photo and old_instance.photo != instance.photo:
        old_instance.photo.delete(save=False)
