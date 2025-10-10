"""
Тесты для apps/core/models.py

Проверка BaseModel и OwnedModel согласно TDD подходу.
"""

from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import OwnedItem, SimpleModel

User = get_user_model()


class TestBaseModel:
    """Тесты для BaseModel"""

    @pytest.mark.django_db
    def test_created_at_auto_set_on_creation(self):
        """Проверка: created_at автоматически устанавливается при создании"""
        obj = SimpleModel.objects.create(name="Test")

        assert obj.created_at is not None
        assert isinstance(obj.created_at, datetime)
        assert obj.created_at <= timezone.now()

    @pytest.mark.django_db
    def test_updated_at_auto_set_on_creation(self):
        """Проверка: updated_at автоматически устанавливается при создании"""
        obj = SimpleModel.objects.create(name="Test")

        assert obj.updated_at is not None
        assert isinstance(obj.updated_at, datetime)
        assert obj.updated_at <= timezone.now()

    @pytest.mark.django_db
    def test_updated_at_changes_on_save(self):
        """Проверка: updated_at обновляется при сохранении"""
        obj = SimpleModel.objects.create(name="Test")
        original_updated = obj.updated_at

        # Небольшая задержка чтобы время изменилось
        import time

        time.sleep(0.01)

        obj.name = "Updated"
        obj.save()

        assert obj.updated_at > original_updated

    @pytest.mark.django_db
    def test_is_active_default_true(self):
        """Проверка: is_active по умолчанию True"""
        obj = SimpleModel.objects.create(name="Test")

        assert obj.is_active is True

    @pytest.mark.django_db
    def test_soft_delete_sets_is_active_false(self):
        """Проверка: soft_delete() устанавливает is_active в False"""
        obj = SimpleModel.objects.create(name="Test")

        obj.soft_delete()

        assert obj.is_active is False
        # Проверяем что изменения сохранены в БД
        obj.refresh_from_db()
        assert obj.is_active is False

    @pytest.mark.django_db
    def test_soft_delete_does_not_delete_from_db(self):
        """Проверка: soft_delete() НЕ удаляет объект из БД"""
        obj = SimpleModel.objects.create(name="Test")
        obj_id = obj.id

        obj.soft_delete()

        # Объект должен остаться в БД
        assert SimpleModel.objects.filter(id=obj_id).exists()

    @pytest.mark.django_db
    def test_restore_sets_is_active_true(self):
        """Проверка: restore() восстанавливает is_active в True"""
        obj = SimpleModel.objects.create(name="Test")
        obj.soft_delete()

        obj.restore()

        assert obj.is_active is True
        # Проверяем что изменения сохранены в БД
        obj.refresh_from_db()
        assert obj.is_active is True

    @pytest.mark.django_db
    def test_default_ordering_by_created_at_desc(self):
        """Проверка: объекты по умолчанию сортируются по -created_at"""
        import time

        obj1 = SimpleModel.objects.create(name="First")
        time.sleep(0.01)
        obj2 = SimpleModel.objects.create(name="Second")
        time.sleep(0.01)
        obj3 = SimpleModel.objects.create(name="Third")

        objects = list(SimpleModel.objects.all())

        assert objects[0] == obj3  # Самый новый первый
        assert objects[1] == obj2
        assert objects[2] == obj1  # Самый старый последний


class TestOwnedModel:
    """Тесты для OwnedModel"""

    @pytest.mark.django_db
    def test_owner_is_required(self, user):
        """Проверка: owner обязателен при создании"""
        from django.db import IntegrityError

        # Попытка создать без owner должна вызвать IntegrityError
        with pytest.raises(IntegrityError):
            OwnedItem.objects.create(title="Test")

    @pytest.mark.django_db
    def test_owner_is_set_correctly(self, user):
        """Проверка: owner корректно устанавливается"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        assert obj.owner == user
        assert obj.owner.email == "user@example.com"

    @pytest.mark.django_db
    def test_inherits_base_model_functionality(self, user):
        """Проверка: OwnedModel наследует функционал BaseModel"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        # Проверяем что есть поля от BaseModel
        assert hasattr(obj, "created_at")
        assert hasattr(obj, "updated_at")
        assert hasattr(obj, "is_active")
        assert obj.is_active is True

    @pytest.mark.django_db
    def test_soft_delete_works_for_owned_model(self, user):
        """Проверка: soft_delete() работает для OwnedModel"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        obj.soft_delete()

        assert obj.is_active is False

    @pytest.mark.django_db
    def test_is_owner_returns_true_for_owner(self, user):
        """Проверка: is_owner() возвращает True для владельца"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        assert obj.is_owner(user) is True

    @pytest.mark.django_db
    def test_is_owner_returns_false_for_non_owner(self, user, another_user):
        """Проверка: is_owner() возвращает False для не-владельца"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        assert obj.is_owner(another_user) is False

    @pytest.mark.django_db
    def test_can_edit_returns_true_for_owner(self, user):
        """Проверка: can_edit() возвращает True для владельца"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        assert obj.can_edit(user) is True

    @pytest.mark.django_db
    def test_can_edit_returns_false_for_non_owner(self, user, another_user):
        """Проверка: can_edit() возвращает False для не-владельца"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        assert obj.can_edit(another_user) is False

    @pytest.mark.django_db
    def test_can_edit_returns_false_for_manager(self, user, manager_user):
        """Проверка: can_edit() возвращает False даже для менеджера (не владельца)"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        # Менеджер НЕ может редактировать чужие объекты
        assert obj.can_edit(manager_user) is False

    @pytest.mark.django_db
    def test_can_delete_returns_true_for_owner(self, user):
        """Проверка: can_delete() возвращает True для владельца"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        assert obj.can_delete(user) is True

    @pytest.mark.django_db
    def test_can_delete_returns_false_for_non_owner(self, user, another_user):
        """Проверка: can_delete() возвращает False для не-владельца"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        assert obj.can_delete(another_user) is False

    @pytest.mark.django_db
    def test_can_delete_returns_false_for_manager(self, user, manager_user):
        """Проверка: can_delete() возвращает False даже для менеджера (не владельца)"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        # Менеджер НЕ может удалять чужие объекты
        assert obj.can_delete(manager_user) is False

    @pytest.mark.django_db
    def test_related_name_pattern(self, user):
        """Проверка: related_name использует %(class)s паттерн"""
        obj = OwnedItem.objects.create(owner=user, title="Test")

        # Должен быть related_name вида "owneditem_owned"
        assert hasattr(user, "owneditem_owned")
        assert obj in user.owneditem_owned.all()
