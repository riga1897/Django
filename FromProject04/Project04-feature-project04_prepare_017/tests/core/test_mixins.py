"""
Тесты для apps/core/mixins.py

Проверяем:
- OwnerFilterMixin
- LoggingMixin
- CacheMixin
"""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from apps.core.mixins import CacheMixin, LoggingMixin, OwnerFilterMixin
from tests.core.models import OwnedItem, SimpleModel

User = get_user_model()


class TestOwnerFilterMixin:
    """Тесты для OwnerFilterMixin"""

    class ServiceWithOwnerFilter(OwnerFilterMixin):
        """Конкретная реализация для тестирования"""

        pass

    @pytest.mark.django_db
    def test_filter_by_owner_returns_none_for_no_user(self):
        """Проверка: filter_by_owner() возвращает пустой QS без пользователя"""
        service = self.ServiceWithOwnerFilter()
        queryset = OwnedItem.objects.all()

        result = service.filter_by_owner(queryset, None)
        assert result.count() == 0

    @pytest.mark.django_db
    def test_filter_by_owner_returns_all_for_staff(self, user):
        """Проверка: filter_by_owner() возвращает все объекты для staff"""
        user.is_staff = True
        user.save()

        service = self.ServiceWithOwnerFilter()
        OwnedItem.objects.create(owner=user, title="Item 1")
        another_user = User.objects.create_user(username="another", email="another@test.com", password="pass")
        OwnedItem.objects.create(owner=another_user, title="Item 2")

        queryset = OwnedItem.objects.all()
        result = service.filter_by_owner(queryset, user)

        assert result.count() == 2

    @pytest.mark.django_db
    def test_filter_by_owner_returns_only_own_for_regular_user(self, user):
        """Проверка: filter_by_owner() возвращает только свои объекты"""
        service = self.ServiceWithOwnerFilter()
        OwnedItem.objects.create(owner=user, title="My Item")
        another_user = User.objects.create_user(username="another", email="another@test.com", password="pass")
        OwnedItem.objects.create(owner=another_user, title="Other's Item")

        queryset = OwnedItem.objects.all()
        result = service.filter_by_owner(queryset, user)

        assert result.count() == 1
        assert result.first().owner == user

    @pytest.mark.django_db
    def test_filter_by_owner_returns_all_for_model_without_owner(self, user):
        """Проверка: filter_by_owner() возвращает все для модели без owner"""
        service = self.ServiceWithOwnerFilter()
        SimpleModel.objects.create(name="Item 1")
        SimpleModel.objects.create(name="Item 2")

        queryset = SimpleModel.objects.all()
        result = service.filter_by_owner(queryset, user)

        assert result.count() == 2

    @pytest.mark.django_db
    def test_can_access_returns_false_for_no_user(self, user):
        """Проверка: can_access() возвращает False без пользователя"""
        service = self.ServiceWithOwnerFilter()
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert service.can_access(item, None) is False

    @pytest.mark.django_db
    def test_can_access_returns_true_for_staff(self, user):
        """Проверка: can_access() возвращает True для staff"""
        staff_user = User.objects.create_user(username="staff", email="staff@test.com", password="pass", is_staff=True)
        service = self.ServiceWithOwnerFilter()
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert service.can_access(item, staff_user) is True

    @pytest.mark.django_db
    def test_can_access_returns_true_for_owner(self, user):
        """Проверка: can_access() возвращает True для владельца"""
        service = self.ServiceWithOwnerFilter()
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert service.can_access(item, user) is True

    @pytest.mark.django_db
    def test_can_access_returns_false_for_non_owner(self, user):
        """Проверка: can_access() возвращает False для не владельца"""
        service = self.ServiceWithOwnerFilter()
        another_user = User.objects.create_user(username="another", email="another@test.com", password="pass")
        item = OwnedItem.objects.create(owner=user, title="Test")

        assert service.can_access(item, another_user) is False

    @pytest.mark.django_db
    def test_can_access_returns_true_for_object_without_owner(self, user):
        """Проверка: can_access() возвращает True для объекта без owner"""
        service = self.ServiceWithOwnerFilter()
        item = SimpleModel.objects.create(name="Test")

        assert service.can_access(item, user) is True


class TestLoggingMixin:
    """Тесты для LoggingMixin"""

    class ServiceWithLogging(LoggingMixin):
        """Конкретная реализация для тестирования"""

        pass

    @pytest.mark.django_db
    @patch("apps.core.mixins.logger")
    def test_log_action_create_logs_info(self, mock_logger, user):
        """Проверка: log_action() логирует CREATE как info"""
        service = self.ServiceWithLogging()
        item = OwnedItem.objects.create(owner=user, title="Test")

        service.log_action("CREATE", item, user)

        mock_logger.info.assert_called_once()
        call_args = str(mock_logger.info.call_args)
        assert "CREATE" in call_args
        assert "OwnedItem" in call_args

    @pytest.mark.django_db
    @patch("apps.core.mixins.logger")
    def test_log_action_view_logs_debug(self, mock_logger, user):
        """Проверка: log_action() логирует VIEW как debug"""
        service = self.ServiceWithLogging()
        item = OwnedItem.objects.create(owner=user, title="Test")

        service.log_action("VIEW", item, user)

        mock_logger.debug.assert_called_once()

    @pytest.mark.django_db
    @patch("apps.core.mixins.logger")
    def test_log_action_includes_user_info(self, mock_logger, user):
        """Проверка: log_action() включает информацию о пользователе"""
        service = self.ServiceWithLogging()
        item = OwnedItem.objects.create(owner=user, title="Test")

        service.log_action("UPDATE", item, user)

        call_args = str(mock_logger.info.call_args)
        assert f"User: {user}" in call_args

    @pytest.mark.django_db
    @patch("apps.core.mixins.logger")
    def test_log_action_without_user_shows_system(self, mock_logger, user):
        """Проверка: log_action() без пользователя показывает System"""
        service = self.ServiceWithLogging()
        item = OwnedItem.objects.create(owner=user, title="Test")

        service.log_action("DELETE", item)

        call_args = str(mock_logger.info.call_args)
        assert "System" in call_args

    @pytest.mark.django_db
    @patch("apps.core.mixins.logger")
    def test_log_action_includes_extra_kwargs(self, mock_logger, user):
        """Проверка: log_action() включает дополнительные kwargs"""
        service = self.ServiceWithLogging()
        item = OwnedItem.objects.create(owner=user, title="Test")

        service.log_action("UPDATE", item, user, reason="Manual edit", count=5)

        call_args = str(mock_logger.info.call_args)
        assert "Extra:" in call_args
        assert "reason" in call_args

    @pytest.mark.django_db
    @patch("apps.core.mixins.logger")
    def test_log_error_logs_error_level(self, mock_logger, user):
        """Проверка: log_error() логирует на уровне error"""
        service = self.ServiceWithLogging()
        error = Exception("Test error")

        service.log_error("CREATE", error, user)

        mock_logger.error.assert_called_once()
        call_args = str(mock_logger.error.call_args)
        assert "ERROR in CREATE" in call_args
        assert "Test error" in call_args

    @pytest.mark.django_db
    @patch("apps.core.mixins.logger")
    def test_log_error_includes_exc_info(self, mock_logger, user):
        """Проверка: log_error() включает exc_info=True"""
        service = self.ServiceWithLogging()
        error = Exception("Test error")

        service.log_error("UPDATE", error, user)

        # Проверяем что exc_info=True был передан
        assert mock_logger.error.call_args.kwargs.get("exc_info") is True

    @pytest.mark.django_db
    @patch("apps.core.mixins.logger")
    def test_log_error_with_extra_kwargs(self, mock_logger, user):
        """Проверка: log_error() включает дополнительные kwargs"""
        service = self.ServiceWithLogging()
        error = Exception("Test error")

        service.log_error("DELETE", error, user, item_id=123)

        call_args = str(mock_logger.error.call_args)
        assert "Extra:" in call_args
        assert "item_id" in call_args


class TestCacheMixin:
    """Тесты для CacheMixin"""

    class ServiceWithCache(CacheMixin):
        """Конкретная реализация для тестирования"""

        pass

    def test_get_cache_key_generates_key_from_args(self):
        """Проверка: get_cache_key() генерирует ключ из args"""
        service = self.ServiceWithCache()

        key = service.get_cache_key("users", "list", 123)

        assert key == "users:list:123"

    def test_get_cache_key_generates_key_from_kwargs(self):
        """Проверка: get_cache_key() генерирует ключ из kwargs"""
        service = self.ServiceWithCache()

        key = service.get_cache_key("users", status="active", page=2)

        # kwargs сортируются, поэтому page идет перед status
        assert key == "users:page=2:status=active"

    def test_get_cache_key_combines_args_and_kwargs(self):
        """Проверка: get_cache_key() комбинирует args и kwargs"""
        service = self.ServiceWithCache()

        key = service.get_cache_key("users", "list", page=1, limit=10)

        assert "users:list:" in key
        assert "page=1" in key
        assert "limit=10" in key

    def test_get_cache_key_sorts_kwargs(self):
        """Проверка: get_cache_key() сортирует kwargs"""
        service = self.ServiceWithCache()

        key1 = service.get_cache_key(z=1, a=2)
        key2 = service.get_cache_key(a=2, z=1)

        assert key1 == key2

    @patch("apps.core.mixins.cache")
    @patch("apps.core.mixins.logger")
    def test_get_from_cache_returns_value_and_logs_hit(self, mock_logger, mock_cache):
        """Проверка: get_from_cache() возвращает значение и логирует HIT"""
        service = self.ServiceWithCache()
        mock_cache.get.return_value = {"data": "test"}

        result = service.get_from_cache("test:key")

        assert result == {"data": "test"}
        mock_cache.get.assert_called_once_with("test:key")
        call_args = str(mock_logger.debug.call_args_list)
        assert "Cache HIT" in call_args

    @patch("apps.core.mixins.cache")
    @patch("apps.core.mixins.logger")
    def test_get_from_cache_returns_none_and_logs_miss(self, mock_logger, mock_cache):
        """Проверка: get_from_cache() возвращает None и логирует MISS"""
        service = self.ServiceWithCache()
        mock_cache.get.return_value = None

        result = service.get_from_cache("test:key")

        assert result is None
        call_args = str(mock_logger.debug.call_args_list)
        assert "Cache MISS" in call_args

    @patch("apps.core.mixins.cache")
    @patch("apps.core.mixins.logger")
    def test_set_cache_saves_value(self, mock_logger, mock_cache):
        """Проверка: set_cache() сохраняет значение в кэш"""
        service = self.ServiceWithCache()

        service.set_cache("test:key", {"data": "value"}, timeout=600)

        mock_cache.set.assert_called_once_with("test:key", {"data": "value"}, 600)
        call_args = str(mock_logger.debug.call_args)
        assert "Cache SET" in call_args
        assert "600s" in call_args

    @patch("apps.core.mixins.cache")
    @patch("apps.core.mixins.logger")
    def test_set_cache_uses_default_timeout(self, mock_logger, mock_cache):
        """Проверка: set_cache() использует дефолтный timeout 300s"""
        service = self.ServiceWithCache()

        service.set_cache("test:key", "value")

        mock_cache.set.assert_called_once_with("test:key", "value", 300)

    @patch("apps.core.mixins.cache")
    @patch("apps.core.mixins.logger")
    def test_invalidate_cache_deletes_key(self, mock_logger, mock_cache):
        """Проверка: invalidate_cache() удаляет ключ"""
        service = self.ServiceWithCache()

        service.invalidate_cache("test:key")

        mock_cache.delete.assert_called_once_with("test:key")
        call_args = str(mock_logger.debug.call_args)
        assert "Cache INVALIDATE" in call_args

    @patch("apps.core.mixins.cache")
    @patch("apps.core.mixins.logger")
    def test_invalidate_cache_pattern_deletes_pattern(self, mock_logger, mock_cache):
        """Проверка: invalidate_cache_pattern() удаляет по паттерну"""
        service = self.ServiceWithCache()
        mock_cache.delete_pattern = MagicMock()

        service.invalidate_cache_pattern("mailing:*")

        mock_cache.delete_pattern.assert_called_once_with("mailing:*")
        call_args = str(mock_logger.debug.call_args)
        assert "Cache INVALIDATE pattern" in call_args

    @patch("apps.core.mixins.cache")
    @patch("apps.core.mixins.logger")
    def test_invalidate_cache_pattern_handles_no_support(self, mock_logger, mock_cache):
        """Проверка: invalidate_cache_pattern() обрабатывает отсутствие метода"""
        service = self.ServiceWithCache()
        # Удаляем метод delete_pattern, чтобы вызвать AttributeError
        delattr(mock_cache, "delete_pattern")

        service.invalidate_cache_pattern("mailing:*")

        call_args = str(mock_logger.warning.call_args)
        assert "does not support pattern deletion" in call_args
