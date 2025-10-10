"""
Тесты для management команд приложения users.
"""

from io import StringIO

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command


class TestCreateManagersGroupCommand:
    """Тесты для команды create_managers_group"""

    @pytest.mark.django_db
    def test_creates_managers_group(self):
        """Проверка: команда создаёт группу Managers"""
        out = StringIO()
        call_command("create_managers_group", stdout=out)

        assert Group.objects.filter(name="Managers").exists()
        output = out.getvalue()
        assert 'Группа "Managers" успешно создана' in output

    @pytest.mark.django_db
    def test_assigns_view_permissions(self):
        """Проверка: команда назначает view permissions для всех моделей"""
        call_command("create_managers_group", stdout=StringIO())

        group = Group.objects.get(name="Managers")
        permissions = group.permissions.all()

        # Проверяем что есть view permissions для User, Recipient, Message, Mailing
        perm_codenames = [p.codename for p in permissions]

        assert "view_user" in perm_codenames
        assert "view_recipient" in perm_codenames
        assert "view_message" in perm_codenames
        assert "view_mailing" in perm_codenames

    @pytest.mark.django_db
    def test_assigns_block_user_permission(self):
        """Проверка: команда назначает permission для блокировки пользователей"""
        call_command("create_managers_group", stdout=StringIO())

        group = Group.objects.get(name="Managers")
        permissions = group.permissions.all()
        perm_codenames = [p.codename for p in permissions]

        # Permission для изменения поля is_active пользователя
        assert "change_user" in perm_codenames

    @pytest.mark.django_db
    def test_assigns_disable_mailing_permission(self):
        """Проверка: команда назначает permission для отключения рассылок"""
        call_command("create_managers_group", stdout=StringIO())

        group = Group.objects.get(name="Managers")
        permissions = group.permissions.all()
        perm_codenames = [p.codename for p in permissions]

        # Custom permission для отключения рассылок
        assert "can_disable_mailing" in perm_codenames

    @pytest.mark.django_db
    def test_assigns_custom_view_permissions(self):
        """Проверка: команда назначает кастомные view_all permissions"""
        call_command("create_managers_group", stdout=StringIO())

        group = Group.objects.get(name="Managers")
        permissions = group.permissions.all()
        perm_codenames = [p.codename for p in permissions]

        # Кастомные permissions для просмотра всех объектов
        assert "can_view_all_recipients" in perm_codenames
        assert "can_view_all_messages" in perm_codenames
        assert "can_view_all_mailings" in perm_codenames

    @pytest.mark.django_db
    def test_does_not_create_duplicate_group(self):
        """Проверка: команда не создаёт дубликат если группа уже существует"""
        # Создаём группу вручную
        Group.objects.create(name="Managers")
        initial_count = Group.objects.filter(name="Managers").count()

        out = StringIO()
        call_command("create_managers_group", stdout=out)

        # Проверяем что группа не дублировалась
        assert Group.objects.filter(name="Managers").count() == initial_count
        output = out.getvalue()
        assert "уже существует" in output

    @pytest.mark.django_db
    def test_updates_permissions_if_group_exists(self):
        """Проверка: команда обновляет permissions если группа уже существует"""
        # Создаём группу без permissions
        group = Group.objects.create(name="Managers")
        assert group.permissions.count() == 0

        # Запускаем команду
        call_command("create_managers_group", stdout=StringIO())

        # Проверяем что permissions добавлены (9 permissions)
        group.refresh_from_db()
        assert group.permissions.count() == 9

    @pytest.mark.django_db
    def test_command_is_idempotent(self):
        """Проверка: команду можно запускать многократно без ошибок"""
        # Запускаем команду дважды
        call_command("create_managers_group", stdout=StringIO())
        call_command("create_managers_group", stdout=StringIO())

        # Должна быть только одна группа
        assert Group.objects.filter(name="Managers").count() == 1

    @pytest.mark.django_db
    def test_command_output_verbose(self):
        """Проверка: команда выводит детальную информацию при --verbose"""
        out = StringIO()
        call_command("create_managers_group", verbosity=2, stdout=out)

        output = out.getvalue()
        # При verbosity=2 должны быть детали о permissions
        assert "permission" in output.lower() or "разрешен" in output.lower()
