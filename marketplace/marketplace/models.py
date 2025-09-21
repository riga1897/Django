from django.db import models
from django.db.models import CASCADE


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Категория", help_text="Введите наименование категории")
    description = models.CharField(max_length=150, verbose_name="Описание категории", help_text="Введите описание категории")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name"]

class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name="Наименование", help_text="Введите наименование товара")
    description = models.CharField(max_length=150, verbose_name="Описание продукта", help_text="Введите описание товара", null=True, blank=True)
    photo = models.ImageField(upload_to="products/photos", blank=True, null=True, verbose_name="Фотография", help_text="Загрузите изображение товара")
    category = models.ForeignKey(Category, on_delete=CASCADE,related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name="Цена", help_text="Введите цену товару")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name"]
