"""
Тесты для apps/core/services.py

Проверяем:
- BaseService (ABC)
- BaseServiceWithErrors
- BaseCRUDService
"""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from apps.core.services import BaseCRUDService, BaseService, BaseServiceWithErrors
from tests.core.models import OwnedItem, SimpleModel

User = get_user_model()


# Конкретная реализация BaseService для тестирования
class ConcreteService(BaseService):
    """Конкретная реализация BaseService для тестов"""

    def validate(self, data: dict) -> bool:
        """Простая валидация - проверяем наличие 'name'"""
        return "name" in data and bool(data["name"])


# Конкретная реализация BaseServiceWithErrors для тестирования
class ConcreteServiceWithErrors(BaseServiceWithErrors):
    """Конкретная реализация BaseServiceWithErrors для тестов"""

    def validate(self, data: dict) -> bool:
        """Простая валидация"""
        if not data:
            self.add_error("Data is empty")
            return False
        return True


class TestBaseService:
    """Тесты для BaseService (ABC)"""

    def test_cannot_instantiate_abstract_class(self):
        """Проверка: нельзя создать экземпляр абстрактного класса"""
        with pytest.raises(TypeError):
            BaseService()

    def test_concrete_implementation_works(self):
        """Проверка: конкретная реализация работает"""
        service = ConcreteService()
        assert service.validate({"name": "test"}) is True
        assert service.validate({}) is False
        assert service.validate({"name": ""}) is False

    def test_validate_is_abstract_method(self):
        """Проверка: validate() является абстрактным методом"""
        # Попытка создать класс без реализации validate должна упасть
        with pytest.raises(TypeError):

            class IncompleteService(BaseService):
                pass

            IncompleteService()


class TestBaseServiceWithErrors:
    """Тесты для BaseServiceWithErrors"""

    def test_init_creates_empty_errors_list(self):
        """Проверка: __init__() создает пустой список ошибок"""
        service = ConcreteServiceWithErrors()
        assert service.errors == []
        assert isinstance(service.errors, list)

    def test_add_error_appends_to_list(self):
        """Проверка: add_error() добавляет ошибку в список"""
        service = ConcreteServiceWithErrors()
        service.add_error("Ошибка 1")
        service.add_error("Ошибка 2")

        assert len(service.errors) == 2
        assert "Ошибка 1" in service.errors
        assert "Ошибка 2" in service.errors

    @patch("apps.core.services.logger")
    def test_add_error_logs_warning(self, mock_logger):
        """Проверка: add_error() логирует warning"""
        service = ConcreteServiceWithErrors()
        service.add_error("Test error")

        mock_logger.warning.assert_called_once_with("Service error: Test error")

    def test_has_errors_returns_true_when_errors_exist(self):
        """Проверка: has_errors() возвращает True когда есть ошибки"""
        service = ConcreteServiceWithErrors()
        assert service.has_errors() is False

        service.add_error("Ошибка")
        assert service.has_errors() is True

    def test_has_errors_returns_false_when_no_errors(self):
        """Проверка: has_errors() возвращает False когда нет ошибок"""
        service = ConcreteServiceWithErrors()
        assert service.has_errors() is False

    def test_clear_errors_removes_all_errors(self):
        """Проверка: clear_errors() удаляет все ошибки"""
        service = ConcreteServiceWithErrors()
        service.add_error("Ошибка 1")
        service.add_error("Ошибка 2")

        service.clear_errors()

        assert service.errors == []
        assert service.has_errors() is False

    def test_get_errors_returns_copy(self):
        """Проверка: get_errors() возвращает копию списка"""
        service = ConcreteServiceWithErrors()
        service.add_error("Ошибка")

        errors = service.get_errors()
        errors.append("Новая ошибка")

        # Изменение копии не должно влиять на оригинал
        assert len(service.errors) == 1
        assert len(errors) == 2


class TestBaseCRUDService:
    """Тесты для BaseCRUDService"""

    @pytest.mark.django_db
    def test_init_sets_model_class(self):
        """Проверка: __init__() устанавливает model_class"""
        service = BaseCRUDService(SimpleModel)
        assert service.model_class == SimpleModel

    @pytest.mark.django_db
    def test_init_initializes_errors_list(self):
        """Проверка: __init__() инициализирует список ошибок (через super)"""
        service = BaseCRUDService(SimpleModel)
        assert hasattr(service, "errors")
        assert service.errors == []

    @pytest.mark.django_db
    def test_validate_rejects_empty_data(self):
        """Проверка: validate() отклоняет пустые данные"""
        service = BaseCRUDService(SimpleModel)

        assert service.validate({}) is False
        assert service.has_errors() is True
        assert "Данные не могут быть пустыми" in service.get_errors()

    @pytest.mark.django_db
    def test_validate_accepts_non_empty_data(self):
        """Проверка: validate() принимает непустые данные"""
        service = BaseCRUDService(SimpleModel)
        assert service.validate({"name": "test"}) is True
        assert service.has_errors() is False

    @pytest.mark.django_db
    def test_get_all_returns_active_objects(self):
        """Проверка: get_all() возвращает только активные объекты"""
        service = BaseCRUDService(SimpleModel)

        obj1 = SimpleModel.objects.create(name="Active")
        obj2 = SimpleModel.objects.create(name="Inactive")
        obj2.soft_delete()

        result = service.get_all()
        assert obj1 in result
        assert obj2 not in result

    @pytest.mark.django_db
    def test_get_all_filters_by_owner_for_regular_user(self, user, another_user):
        """Проверка: get_all() фильтрует по owner для обычного пользователя"""
        service = BaseCRUDService(OwnedItem)

        my_item = OwnedItem.objects.create(owner=user, title="My Item")
        other_item = OwnedItem.objects.create(owner=another_user, title="Other Item")

        result = service.get_all(user)
        assert my_item in result
        assert other_item not in result

    @pytest.mark.django_db
    def test_get_all_shows_all_for_staff_user(self, user, another_user, manager_user):
        """Проверка: get_all() показывает все объекты для staff пользователя"""
        service = BaseCRUDService(OwnedItem)

        item1 = OwnedItem.objects.create(owner=user, title="Item 1")
        item2 = OwnedItem.objects.create(owner=another_user, title="Item 2")

        result = service.get_all(manager_user)
        assert item1 in result
        assert item2 in result

    @pytest.mark.django_db
    def test_get_by_id_returns_object(self, user):
        """Проверка: get_by_id() возвращает объект по ID"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=user, title="Test")

        result = service.get_by_id(item.id, user)
        assert result == item

    @pytest.mark.django_db
    def test_get_by_id_returns_none_for_nonexistent(self, user):
        """Проверка: get_by_id() возвращает None для несуществующего ID"""
        service = BaseCRUDService(OwnedItem)

        result = service.get_by_id(999, user)
        assert result is None
        assert service.has_errors() is True
        assert "Объект с ID 999 не найден" in service.get_errors()

    @pytest.mark.django_db
    def test_get_by_id_respects_ownership(self, user, another_user):
        """Проверка: get_by_id() учитывает права владения"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=another_user, title="Other's Item")

        result = service.get_by_id(item.id, user)
        assert result is None  # user не может видеть чужой объект

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_create_success(self, mock_logger):
        """Проверка: create() создает объект"""
        service = BaseCRUDService(SimpleModel)

        result = service.create({"name": "Test Object"})
        assert result is not None
        assert result.name == "Test Object"
        assert SimpleModel.objects.filter(name="Test Object").exists()

        mock_logger.info.assert_called_once()

    @pytest.mark.django_db
    def test_create_with_owner(self, user):
        """Проверка: create() устанавливает owner для OwnedModel"""
        service = BaseCRUDService(OwnedItem)

        result = service.create({"title": "Test"}, owner=user)
        assert result is not None
        assert result.owner == user
        assert result.title == "Test"

    @pytest.mark.django_db
    def test_create_fails_with_invalid_data(self):
        """Проверка: create() возвращает None при невалидных данных"""
        service = BaseCRUDService(SimpleModel)

        result = service.create({})
        assert result is None
        assert service.has_errors() is True

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_create_handles_exception(self, mock_logger):
        """Проверка: create() обрабатывает исключения"""
        service = BaseCRUDService(SimpleModel)

        # Попытка создать с невалидным полем вызовет ошибку
        result = service.create({"invalid_field": "value"})
        assert result is None
        assert service.has_errors() is True

        mock_logger.error.assert_called_once()

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_update_success(self, mock_logger, user):
        """Проверка: update() обновляет объект"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=user, title="Old Title")

        result = service.update(item.id, {"title": "New Title"}, user)
        assert result is not None
        assert result.title == "New Title"

        mock_logger.info.assert_called_once()

    @pytest.mark.django_db
    def test_update_fails_for_nonexistent_object(self, user):
        """Проверка: update() возвращает None для несуществующего объекта"""
        service = BaseCRUDService(OwnedItem)

        result = service.update(999, {"title": "New"}, user)
        assert result is None
        assert service.has_errors() is True

    @pytest.mark.django_db
    def test_update_fails_with_invalid_data(self, user):
        """Проверка: update() возвращает None при невалидных данных"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=user, title="Test")

        result = service.update(item.id, {}, user)
        assert result is None
        assert service.has_errors() is True
        assert "Данные не могут быть пустыми" in service.get_errors()

    @pytest.mark.django_db
    def test_update_fails_without_edit_permission(self, user, another_user):
        """Проверка: update() запрещает редактирование без прав"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=another_user, title="Other's Item")

        result = service.update(item.id, {"title": "Hacked"}, user)
        assert result is None
        assert "Нет прав на редактирование" in service.get_errors()[0]

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_update_logs_permission_warning(self, mock_logger, user, another_user):
        """Проверка: update() логирует попытку редактирования без прав"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=another_user, title="Other's Item")

        service.update(item.id, {"title": "Hacked"}, user)
        # Проверяем что есть вызов warning с нужным сообщением
        # (add_error тоже вызывает warning, поэтому их будет 2)
        warning_calls = [call for call in mock_logger.warning.call_args_list if "attempted to edit" in str(call)]
        assert len(warning_calls) == 1

    @pytest.mark.django_db
    def test_update_manager_cannot_edit_others(self, another_user, manager_user):
        """Проверка: update() менеджер НЕ может редактировать чужие объекты"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=another_user, title="User's Item")

        result = service.update(item.id, {"title": "Manager Edit"}, manager_user)
        assert result is None
        assert "Нет прав на редактирование" in service.get_errors()[0]

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_update_handles_save_exception(self, mock_logger, user):
        """Проверка: update() обрабатывает исключения при save()"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=user, title="Test")

        # Мокаем save() чтобы вызвать исключение
        with patch.object(OwnedItem, "save", side_effect=Exception("Database error")):
            result = service.update(item.id, {"title": "New"}, user)

            assert result is None
            assert service.has_errors() is True
            assert "Ошибка при обновлении" in service.get_errors()[0]
            mock_logger.error.assert_called_once()

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_delete_soft_delete_success(self, mock_logger, user):
        """Проверка: delete() выполняет мягкое удаление"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=user, title="To Delete")

        result = service.delete(item.id, user, soft=True)
        assert result is True

        item.refresh_from_db()
        assert item.is_active is False

        mock_logger.info.assert_called_once()
        assert "Soft deleted" in mock_logger.info.call_args[0][0]

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_delete_hard_delete_success(self, mock_logger, user):
        """Проверка: delete() выполняет жесткое удаление"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=user, title="To Delete")
        item_id = item.id

        result = service.delete(item.id, user, soft=False)
        assert result is True
        assert not OwnedItem.objects.filter(id=item_id).exists()

        mock_logger.info.assert_called_once()
        assert "Hard deleted" in mock_logger.info.call_args[0][0]

    @pytest.mark.django_db
    def test_delete_fails_for_nonexistent_object(self, user):
        """Проверка: delete() возвращает False для несуществующего объекта"""
        service = BaseCRUDService(OwnedItem)

        result = service.delete(999, user)
        assert result is False
        assert service.has_errors() is True

    @pytest.mark.django_db
    def test_delete_fails_without_permission(self, user, another_user):
        """Проверка: delete() запрещает удаление без прав"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=another_user, title="Other's Item")

        result = service.delete(item.id, user)
        assert result is False
        assert "Нет прав на удаление" in service.get_errors()[0]

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_delete_logs_permission_warning(self, mock_logger, user, another_user):
        """Проверка: delete() логирует попытку удаления без прав"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=another_user, title="Other's Item")

        service.delete(item.id, user)
        # Проверяем что есть вызов warning с нужным сообщением
        # (add_error тоже вызывает warning, поэтому их будет 2)
        warning_calls = [call for call in mock_logger.warning.call_args_list if "attempted to delete" in str(call)]
        assert len(warning_calls) == 1

    @pytest.mark.django_db
    def test_delete_manager_cannot_delete_others(self, another_user, manager_user):
        """Проверка: delete() менеджер НЕ может удалять чужие объекты"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=another_user, title="User's Item")

        result = service.delete(item.id, manager_user)
        assert result is False
        assert "Нет прав на удаление" in service.get_errors()[0]

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_delete_handles_soft_delete_exception(self, mock_logger, user):
        """Проверка: delete() обрабатывает исключения при soft_delete()"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=user, title="Test")

        # Мокаем soft_delete() чтобы вызвать исключение
        with patch.object(OwnedItem, "soft_delete", side_effect=Exception("Deletion error")):
            result = service.delete(item.id, user, soft=True)

            assert result is False
            assert service.has_errors() is True
            assert "Ошибка при удалении" in service.get_errors()[0]
            mock_logger.error.assert_called_once()

    @pytest.mark.django_db
    @patch("apps.core.services.logger")
    def test_delete_handles_hard_delete_exception(self, mock_logger, user):
        """Проверка: delete() обрабатывает исключения при hard delete"""
        service = BaseCRUDService(OwnedItem)
        item = OwnedItem.objects.create(owner=user, title="Test")

        # Мокаем delete() чтобы вызвать исключение
        with patch.object(OwnedItem, "delete", side_effect=Exception("Hard delete error")):
            result = service.delete(item.id, user, soft=False)

            assert result is False
            assert service.has_errors() is True
            assert "Ошибка при удалении" in service.get_errors()[0]
            mock_logger.error.assert_called_once()

    @pytest.mark.django_db
    def test_count_returns_correct_number(self, user):
        """Проверка: count() возвращает правильное количество"""
        service = BaseCRUDService(OwnedItem)

        OwnedItem.objects.create(owner=user, title="Item 1")
        OwnedItem.objects.create(owner=user, title="Item 2")
        OwnedItem.objects.create(owner=user, title="Item 3")

        assert service.count(user) == 3

    @pytest.mark.django_db
    def test_count_respects_ownership(self, user, another_user):
        """Проверка: count() учитывает права владения"""
        service = BaseCRUDService(OwnedItem)

        OwnedItem.objects.create(owner=user, title="My Item 1")
        OwnedItem.objects.create(owner=user, title="My Item 2")
        OwnedItem.objects.create(owner=another_user, title="Other's Item")

        assert service.count(user) == 2

    @pytest.mark.django_db
    def test_count_excludes_inactive(self, user):
        """Проверка: count() не считает неактивные объекты"""
        service = BaseCRUDService(OwnedItem)

        OwnedItem.objects.create(owner=user, title="Active")
        inactive = OwnedItem.objects.create(owner=user, title="Inactive")
        inactive.soft_delete()

        assert service.count(user) == 1
