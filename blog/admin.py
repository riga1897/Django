from django.contrib import admin

from .models import BlogPost


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'views_count', 'created_at')  # 👈 Добавляем статус публикации
    list_filter = ('is_published', 'created_at')  # Фильтр по статусу
    list_editable = ('is_published',)  # Быстрое редактирование статуса
    search_fields = ('title', 'content')  # Поиск по заголовку и содержанию


admin.site.register(BlogPost, BlogPostAdmin)
