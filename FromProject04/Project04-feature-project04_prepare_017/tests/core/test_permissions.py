"""
Тесты для apps/core/permissions.py

Проверяем:
- BasePermissionChecker
- has_perm()
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group

from apps.core.permissions import BasePermissionChecker, has_perm
from tests.core.models import OwnedItem, SimpleModel

User = get_user_model()


class TestBasePermissionChecker:
    """Тесты для BasePermissionChecker"""

    @pytest.mark.django_db
    def test_is_owner_returns_true_for_owner(self, user):
        """Проверка: is_owner() возвращает True для владельца"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.is_owner(item, user) is True

    @pytest.mark.django_db
    def test_is_owner_returns_false_for_non_owner(self, user):
        """Проверка: is_owner() возвращает False для не владельца"""
        another_user = User.objects.create_user(username="another", email="another@test.com", password="pass")
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.is_owner(item, another_user) is False

    @pytest.mark.django_db
    def test_is_owner_returns_false_for_unauthenticated(self, user):
        """Проверка: is_owner() возвращает False для неаутентифицированного"""
        item = OwnedItem.objects.create(owner=user, title="Test")
        anon = AnonymousUser()

        assert BasePermissionChecker.is_owner(item, anon) is False

    @pytest.mark.django_db
    def test_is_owner_returns_false_for_none_user(self, user):
        """Проверка: is_owner() возвращает False для None"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.is_owner(item, None) is False

    @pytest.mark.django_db
    def test_is_owner_returns_false_for_object_without_owner(self, user):
        """Проверка: is_owner() возвращает False для объекта без owner"""
        item = SimpleModel.objects.create(name="Test")

        assert BasePermissionChecker.is_owner(item, user) is False

    @pytest.mark.django_db
    def test_is_manager_returns_true_for_staff(self):
        """Проверка: is_manager() возвращает True для is_staff"""
        user = User.objects.create_user(username="staff", email="staff@test.com", password="pass", is_staff=True)

        assert BasePermissionChecker.is_manager(user) is True

    @pytest.mark.django_db
    def test_is_manager_returns_true_for_superuser(self):
        """Проверка: is_manager() возвращает True для superuser"""
        user = User.objects.create_user(username="super", email="super@test.com", password="pass", is_superuser=True)

        assert BasePermissionChecker.is_manager(user) is True

    @pytest.mark.django_db
    def test_is_manager_returns_true_for_managers_group(self, user):
        """Проверка: is_manager() возвращает True для группы Менеджеры"""
        managers_group = Group.objects.create(name="Менеджеры")
        user.groups.add(managers_group)

        assert BasePermissionChecker.is_manager(user) is True

    @pytest.mark.django_db
    def test_is_manager_returns_false_for_regular_user(self, user):
        """Проверка: is_manager() возвращает False для обычного пользователя"""
        assert BasePermissionChecker.is_manager(user) is False

    @pytest.mark.django_db
    def test_is_manager_returns_false_for_unauthenticated(self):
        """Проверка: is_manager() возвращает False для неаутентифицированного"""
        anon = AnonymousUser()

        assert BasePermissionChecker.is_manager(anon) is False

    @pytest.mark.django_db
    def test_is_manager_returns_false_for_none(self):
        """Проверка: is_manager() возвращает False для None"""
        assert BasePermissionChecker.is_manager(None) is False

    @pytest.mark.django_db
    def test_can_view_returns_true_for_manager(self, user):
        """Проверка: can_view() возвращает True для менеджера"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_view(item, manager) is True

    @pytest.mark.django_db
    def test_can_view_returns_true_for_owner(self, user):
        """Проверка: can_view() возвращает True для владельца"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_view(item, user) is True

    @pytest.mark.django_db
    def test_can_view_returns_false_for_non_owner(self, user):
        """Проверка: can_view() возвращает False для не владельца"""
        another_user = User.objects.create_user(username="another", email="another@test.com", password="pass")
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_view(item, another_user) is False

    @pytest.mark.django_db
    def test_can_edit_returns_true_for_owner(self, user):
        """Проверка: can_edit() возвращает True для владельца"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_edit(item, user) is True

    @pytest.mark.django_db
    def test_can_edit_returns_false_for_non_owner(self, user):
        """Проверка: can_edit() возвращает False для не владельца"""
        another_user = User.objects.create_user(username="another", email="another@test.com", password="pass")
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_edit(item, another_user) is False

    @pytest.mark.django_db
    def test_can_edit_returns_false_for_manager(self, user):
        """Проверка: can_edit() возвращает False для менеджера (согласно ТЗ)"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_edit(item, manager) is False

    @pytest.mark.django_db
    def test_can_delete_returns_true_for_owner(self, user):
        """Проверка: can_delete() возвращает True для владельца"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_delete(item, user) is True

    @pytest.mark.django_db
    def test_can_delete_returns_false_for_non_owner(self, user):
        """Проверка: can_delete() возвращает False для не владельца"""
        another_user = User.objects.create_user(username="another", email="another@test.com", password="pass")
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_delete(item, another_user) is False

    @pytest.mark.django_db
    def test_can_delete_returns_false_for_manager(self, user):
        """Проверка: can_delete() возвращает False для менеджера (согласно ТЗ)"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert BasePermissionChecker.can_delete(item, manager) is False

    @pytest.mark.django_db
    def test_can_disable_mailing_returns_true_for_manager(self):
        """Проверка: can_disable_mailing() возвращает True для менеджера"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )

        assert BasePermissionChecker.can_disable_mailing(manager) is True

    @pytest.mark.django_db
    def test_can_disable_mailing_returns_false_for_regular_user(self, user):
        """Проверка: can_disable_mailing() возвращает False для обычного пользователя"""
        assert BasePermissionChecker.can_disable_mailing(user) is False

    @pytest.mark.django_db
    def test_can_block_user_returns_true_for_manager(self):
        """Проверка: can_block_user() возвращает True для менеджера"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )

        assert BasePermissionChecker.can_block_user(manager) is True

    @pytest.mark.django_db
    def test_can_block_user_returns_false_for_regular_user(self, user):
        """Проверка: can_block_user() возвращает False для обычного пользователя"""
        assert BasePermissionChecker.can_block_user(user) is False


class TestHasPerm:
    """Тесты для функции has_perm()"""

    @pytest.mark.django_db
    def test_has_perm_returns_false_for_unauthenticated(self, user):
        """Проверка: has_perm() возвращает False для неаутентифицированного"""
        anon = AnonymousUser()
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(anon, "view", item) is False

    @pytest.mark.django_db
    def test_has_perm_returns_false_for_none_user(self, user):
        """Проверка: has_perm() возвращает False для None"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(None, "view", item) is False

    @pytest.mark.django_db
    def test_has_perm_view_returns_true_for_owner(self, user):
        """Проверка: has_perm('view') возвращает True для владельца"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(user, "view", item) is True

    @pytest.mark.django_db
    def test_has_perm_view_returns_true_for_manager(self, user):
        """Проверка: has_perm('view') возвращает True для менеджера"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(manager, "view", item) is True

    @pytest.mark.django_db
    def test_has_perm_edit_returns_true_for_owner(self, user):
        """Проверка: has_perm('edit') возвращает True для владельца"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(user, "edit", item) is True

    @pytest.mark.django_db
    def test_has_perm_edit_returns_false_for_manager(self, user):
        """Проверка: has_perm('edit') возвращает False для менеджера"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(manager, "edit", item) is False

    @pytest.mark.django_db
    def test_has_perm_delete_returns_true_for_owner(self, user):
        """Проверка: has_perm('delete') возвращает True для владельца"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(user, "delete", item) is True

    @pytest.mark.django_db
    def test_has_perm_delete_returns_false_for_manager(self, user):
        """Проверка: has_perm('delete') возвращает False для менеджера"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(manager, "delete", item) is False

    @pytest.mark.django_db
    def test_has_perm_disable_mailing_returns_true_for_manager(self):
        """Проверка: has_perm('disable_mailing') возвращает True для менеджера"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )

        assert has_perm(manager, "disable_mailing") is True

    @pytest.mark.django_db
    def test_has_perm_disable_mailing_returns_false_for_regular_user(self, user):
        """Проверка: has_perm('disable_mailing') возвращает False для обычного пользователя"""
        assert has_perm(user, "disable_mailing") is False

    @pytest.mark.django_db
    def test_has_perm_block_user_returns_true_for_manager(self):
        """Проверка: has_perm('block_user') возвращает True для менеджера"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )

        assert has_perm(manager, "block_user") is True

    @pytest.mark.django_db
    def test_has_perm_block_user_returns_false_for_regular_user(self, user):
        """Проверка: has_perm('block_user') возвращает False для обычного пользователя"""
        assert has_perm(user, "block_user") is False

    @pytest.mark.django_db
    def test_has_perm_returns_false_for_unknown_permission(self, user):
        """Проверка: has_perm() возвращает False для неизвестного права"""
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert has_perm(user, "unknown_permission", item) is False

    @pytest.mark.django_db
    def test_has_perm_works_without_obj_for_disable_mailing(self):
        """Проверка: has_perm() работает без obj для disable_mailing"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )

        assert has_perm(manager, "disable_mailing") is True

    @pytest.mark.django_db
    def test_has_perm_works_without_obj_for_block_user(self):
        """Проверка: has_perm() работает без obj для block_user"""
        manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", is_staff=True
        )

        assert has_perm(manager, "block_user") is True
