from django.core.cache import cache

from config.settings import CACHE_ENABLED
from marketplace.models import Product


def get_products(user):
        if user.is_authenticated and (
                user.is_staff or user.groups.filter(name="Модератор продуктов").exists()
        ):  # type: ignore[attr-defined]
            # Staff или модераторы видят все продукты
            queryset = Product.objects.all()  # type: ignore[attr-defined]
            products = get_products_from_cache(queryset)
        elif user.is_authenticated:
            # Авторизованные пользователи видят опубликованные ИЛИ свои собственные
            queryset = Product.objects.filter(Q(is_published=True) | Q(owner=user))  # type: ignore[attr-defined]
            products = get_products_from_cache(queryset)
        else:
            # Неавторизованные видят только опубликованные
            queryset = Product.objects.filter(is_published=True)  # type: ignore[attr-defined]
            products = get_products_from_cache(queryset)

        return products


def get_products_from_cache(queryset):
    if not CACHE_ENABLED:
        to_return = queryset
    else:
        key = "product_list"
        products = cache.get(key)
        if products is not None:
            to_return = queryset
        else:
            products = queryset
            cache.set(key, products)
            to_return = products
    return to_return
