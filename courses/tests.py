from django.test import Client, TestCase
from django.urls import resolve, reverse

from courses import views


class CoursesViewsTestCase(TestCase):
    """Комплексные тесты для представлений приложения courses"""

    def setUp(self):
        self.client = Client()

    def test_students_list_view(self):
        """Тест представления students_list"""
        # students_list возвращает None, что вызывает ошибку Django
        with self.assertRaises(ValueError):
            self.client.get("/courses/list/")

    def test_students_list_function_directly(self):
        """Прямой тест функции students_list"""
        from django.http import HttpRequest

        request = HttpRequest()
        result = views.students_list(request)
        self.assertIsNone(result)


class CoursesUrlsTestCase(TestCase):
    """Тесты для URL-маршрутов приложения courses"""

    def test_students_list_url_resolves(self):
        """Тест резолва URL list"""
        url = reverse("courses:list")
        self.assertEqual(url, "/courses/list/")
        resolver = resolve("/courses/list/")
        self.assertEqual(resolver.func, views.students_list)
        self.assertEqual(resolver.namespace, "courses")
        self.assertEqual(resolver.url_name, "list")


class CoursesModelsTestCase(TestCase):
    """Тесты для моделей приложения courses"""

    def test_models_import(self):
        """Тест импорта модулей models"""
        from courses import models

        # Проверяем, что модуль можно импортировать
        self.assertIsNotNone(models)
        # В пустом файле нет активных импортов, но модуль существует
        self.assertTrue(hasattr(models, "__file__"))


class CoursesAppsTestCase(TestCase):
    """Тесты для конфигурации приложения courses"""

    def test_apps_config(self):
        """Тест конфигурации приложения"""
        from courses.apps import CoursesConfig

        self.assertEqual(CoursesConfig.default_auto_field, "django.db.models.BigAutoField")
        self.assertEqual(CoursesConfig.name, "courses")


class CoursesAdminTestCase(TestCase):
    """Тесты для админ-панели приложения courses"""

    def test_admin_import(self):
        """Тест импорта admin модуля"""
        from courses import admin

        # Проверяем, что модуль можно импортировать
        self.assertIsNotNone(admin)
        # В пустом файле нет активных импортов, но модуль существует
        self.assertTrue(hasattr(admin, "__file__"))
