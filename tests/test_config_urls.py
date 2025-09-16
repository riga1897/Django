from django.test import TestCase, Client
from django.urls import reverse, resolve  # , NoReverseMatch
# from django.contrib import admin


class ConfigUrlsTestCase(TestCase):
    """Тесты для главных URL-маршрутов проекта config"""

    def setUp(self):
        self.client = Client()

    def test_admin_url_resolves(self):
        """Тест резолва URL админ-панели"""
        url = reverse('admin:index')
        self.assertEqual(url, '/admin/')
        resolver = resolve('/admin/')
        # Проверяем что URL разрешается корректно
        self.assertEqual(resolver.url_name, 'index')
        self.assertEqual(resolver.namespace, 'admin')

    def test_students_namespace_resolves(self):
        """Тест доступности namespace students"""
        # Проверяем что можем резолвить URL из students namespace
        url = reverse('students:about')
        self.assertEqual(url, '/students/about/')

        # Проверяем резолв обратно
        resolver = resolve('/students/about/')
        self.assertEqual(resolver.namespace, 'students')

    def test_courses_namespace_resolves(self):
        """Тест доступности namespace courses"""
        # Проверяем что можем резолвить URL из courses namespace
        url = reverse('courses:list')
        self.assertEqual(url, '/courses/list/')

        # Проверяем резолв обратно
        resolver = resolve('/courses/list/')
        self.assertEqual(resolver.namespace, 'courses')

    def test_admin_url_response(self):
        """Тест ответа от админ-панели"""
        response = self.client.get('/admin/')
        # Админ-панель должна редиректить на логин
        self.assertEqual(response.status_code, 302)

    def test_students_urls_included(self):
        """Тест включения students URLs"""
        # Тестируем несколько URL из students app
        response = self.client.get('/students/about/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/students/contact/')
        self.assertEqual(response.status_code, 200)

    def test_courses_urls_included(self):
        """Тест включения courses URLs"""
        # courses/views.students_list возвращает None, что вызывает ошибку Django
        with self.assertRaises(ValueError):
            self.client.get('/courses/list/')

    def test_root_url_not_configured(self):
        """Тест что корневой URL не настроен"""
        # Корневой URL закомментирован в config/urls.py
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_url(self):
        """Тест несуществующего URL"""
        response = self.client.get('/nonexistent/')
        self.assertEqual(response.status_code, 404)
