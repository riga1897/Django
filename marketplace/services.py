from django.core.cache import cache
from django.db.models import Q

from config.settings import CACHE_ENABLED
from marketplace.models import Product, Category


def get_products(user, category_id=None):
    # Создаем уникальный ключ для кэша на основе прав пользователя и категории
    cache_key_parts = []

    if category_id:
        cache_key_parts.append(f"category_{category_id}")

    if user.is_authenticated and (
            user.is_staff or user.groups.filter(name="Модератор продуктов").exists()):  # type: ignore[attr-defined]
        # Staff или модераторы видят все продукты
        cache_key_parts.append(f"staff_{user.id}")
        queryset = Product.objects.all()  # type: ignore[attr-defined]
        # products = get_products_from_cache(queryset)
    elif user.is_authenticated:
        # Авторизованные пользователи видят опубликованные ИЛИ свои собственные
        cache_key_parts.append(f"user_{user.id}")
        queryset = Product.objects.filter(Q(is_published=True) | Q(owner=user))  # type: ignore[attr-defined]
        # products = get_products_from_cache(queryset)
    else:
        # Неавторизованные видят только опубликованные
        cache_key_parts.append("anonymous")
        queryset = Product.objects.filter(is_published=True)  # type: ignore[attr-defined]
        # products = get_products_from_cache(queryset)

    # Дополнительная фильтрация по категории, если указана
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    cache_key = "_".join(cache_key_parts)

    return get_products_from_cache(queryset, cache_key)


# def get_products_by_category(user, category_id):
#     """
#     Сервисная функция для получения продуктов по ID категории
#     """
#     try:
#         category = Category.objects.get(id=category_id)
#     except Category.DoesNotExist:
#         return Product.objects.none()
#
#     return get_products(user, category_id)


def get_products_from_cache(queryset, cache_key):
    """
    Универсальная функция кэширования
    """
    if not CACHE_ENABLED:
        to_return = queryset
    else:
        # Нормализуем ключ
        normalized_key = f"products_{cache_key}"

        # Пытаемся получить данные из кэша
        cached_products = cache.get(normalized_key)

        if cached_products is not None:
            # Восстанавливаем queryset
            to_return = cached_products
        else:
            # Если кэш пуст, выполняем запрос и сохраняем результат
            cached_products = queryset
            cache.set(normalized_key, cached_products)
            to_return = cached_products
    return to_return
