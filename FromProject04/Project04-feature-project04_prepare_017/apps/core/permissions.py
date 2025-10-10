from typing import Any


class BasePermissionChecker:
    """
    Базовый класс для проверки прав доступа.

    Используется для централизованной логики проверки прав,
    особенно важно для разделения прав между Пользователями и Менеджерами.
    """

    @staticmethod
    def is_owner(obj: Any, user: Any) -> bool:
        """
        Проверяет, является ли пользователь владельцем объекта.

        Args:
            obj: Объект для проверки
            user: Пользователь

        Returns:
            True если пользователь - владелец
        """
        if not user or not user.is_authenticated:
            return False

        if hasattr(obj, "owner"):
            return bool(obj.owner == user)

        return False

    @staticmethod
    def is_manager(user: Any) -> bool:
        """
        Проверяет, является ли пользователь менеджером.

        Менеджер определяется как:
        - Член группы "Менеджеры"
        - ИЛИ имеет is_staff = True

        Args:
            user: Пользователь

        Returns:
            True если пользователь - менеджер
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        return bool(user.groups.filter(name="Менеджеры").exists())

    @staticmethod
    def can_view(obj: Any, user: Any) -> bool:
        """
        Может ли пользователь просматривать объект.

        Логика:
        - Менеджеры видят все
        - Пользователи видят только свои объекты

        Args:
            obj: Объект
            user: Пользователь

        Returns:
            True если доступ разрешен
        """
        if BasePermissionChecker.is_manager(user):
            return True

        return BasePermissionChecker.is_owner(obj, user)

    @staticmethod
    def can_edit(obj: Any, user: Any) -> bool:
        """
        Может ли пользователь редактировать объект.

        Логика:
        - Только владелец может редактировать
        - Менеджеры НЕ могут редактировать чужие объекты (согласно ТЗ)

        Args:
            obj: Объект
            user: Пользователь

        Returns:
            True если редактирование разрешено
        """
        return BasePermissionChecker.is_owner(obj, user)

    @staticmethod
    def can_delete(obj: Any, user: Any) -> bool:
        """
        Может ли пользователь удалить объект.

        Логика:
        - Только владелец может удалить
        - Менеджеры НЕ могут удалять чужие объекты (согласно ТЗ)

        Args:
            obj: Объект
            user: Пользователь

        Returns:
            True если удаление разрешено
        """
        return BasePermissionChecker.is_owner(obj, user)

    @staticmethod
    def can_disable_mailing(user: Any) -> bool:
        """
        Может ли пользователь отключать рассылки.

        Только менеджеры могут отключать рассылки (согласно ТЗ).

        Args:
            user: Пользователь

        Returns:
            True если пользователь может отключать рассылки
        """
        return BasePermissionChecker.is_manager(user)

    @staticmethod
    def can_block_user(user: Any) -> bool:
        """
        Может ли пользователь блокировать других пользователей.

        Только менеджеры могут блокировать пользователей (согласно ТЗ).

        Args:
            user: Пользователь

        Returns:
            True если пользователь может блокировать других
        """
        return BasePermissionChecker.is_manager(user)


def has_perm(user: Any, permission: str, obj: Any = None) -> bool:
    """
    Универсальная функция проверки прав.

    Args:
        user: Пользователь
        permission: Название права (например, 'view', 'edit', 'delete')
        obj: Объект, для которого проверяются права (опционально)

    Returns:
        True если право есть

    Example:
        if has_perm(request.user, 'edit', mailing):
            # Пользователь может редактировать рассылку
    """
    if not user or not user.is_authenticated:
        return False

    permission_map = {
        "view": BasePermissionChecker.can_view,
        "edit": BasePermissionChecker.can_edit,
        "delete": BasePermissionChecker.can_delete,
        "disable_mailing": lambda o, u: BasePermissionChecker.can_disable_mailing(u),
        "block_user": lambda o, u: BasePermissionChecker.can_block_user(u),
    }

    check_function = permission_map.get(permission)
    if not check_function:
        return False

    if obj:
        return check_function(obj, user)
    else:
        return check_function(None, user)
