from django.core.cache import cache
from django.db.models import Case, Q, When

from config.settings import CACHE_ENABLED
from marketplace.models import Product


def get_products(user, category_id=None, category_ids=None):
    # Создаем уникальный ключ для кэша на основе прав пользователя и категории
    cache_key_parts = []

    # Поддержка как одной категории (category_id), так и нескольких (category_ids)
    if category_ids:
        cache_key_parts.append(f"categories_{'_'.join(map(str, sorted(category_ids)))}")
    elif category_id:
        cache_key_parts.append(f"category_{category_id}")

    if user.is_authenticated and (user.is_staff or user.groups.filter(name="Модератор продуктов").exists()):  # type: ignore[attr-defined]
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

    # Дополнительная фильтрация по категориям
    if category_ids:
        # Фильтрация по нескольким категориям (OR)
        queryset = queryset.filter(category_id__in=category_ids)
    elif category_id:
        # Фильтрация по одной категории (для обратной совместимости)
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
    Улучшенная функция кэширования
    Кэширует список ID продуктов вместо QuerySet объектов
    для лучшей производительности и совместимости с разными бэкендами
    """
    if not CACHE_ENABLED:
        return queryset

    # Нормализуем ключ
    normalized_key = f"products_{cache_key}"

    # Пытаемся получить ID из кэша
    cached_product_ids = cache.get(normalized_key)

    if cached_product_ids is not None:
        # Восстанавливаем queryset из сохранённых ID
        if not cached_product_ids:
            return Product.objects.none()  # type: ignore[attr-defined]

        # Сохраняем порядок из кэша используя Case/When
        preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(cached_product_ids)])
        return Product.objects.filter(id__in=cached_product_ids).order_by(preserved_order)  # type: ignore[attr-defined]

    # Если кэш пуст, выполняем запрос и сохраняем ID
    # Вычисляем queryset и получаем список ID
    product_ids = list(queryset.values_list("id", flat=True))

    # Сохраняем в кэш список ID (легковесный и сериализуемый)
    cache.set(normalized_key, product_ids, timeout=300)  # 5 минут кэша

    # Возвращаем исходный queryset
    return queryset
