from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import resolve, reverse

from students import views


class StudentsViewsTestCase(TestCase):
    """Комплексные тесты для представлений приложения students"""

    def setUp(self):
        self.client = Client()

    def test_show_data_get_request(self):
        """Тест представления show_data для GET-запроса"""
        # В реальном коде show_data пытается рендерить app/data.html, но шаблона нет
        # Поэтому возникает TemplateDoesNotExist ошибка
        from django.template import TemplateDoesNotExist

        with self.assertRaises(TemplateDoesNotExist):
            self.client.get("/students/show_data/")

    def test_show_data_post_request(self):
        """Тест представления show_data для POST-запроса"""
        # show_data возвращает None для POST-запросов, что вызывает ошибку Django
        with self.assertRaises(ValueError):
            self.client.post("/students/show_data/")

    def test_show_data_function_directly(self):
        """Прямой тест функции show_data"""
        from django.http import HttpRequest
        from django.template import TemplateDoesNotExist

        # GET запрос
        request = HttpRequest()
        request.method = "GET"
        # Функция пытается рендерить несуществующий шаблон
        with self.assertRaises(TemplateDoesNotExist):
            views.show_data(request)

        # POST запрос
        request.method = "POST"
        result = views.show_data(request)
        self.assertIsNone(result)

    def test_submit_data_get_request(self):
        """Тест представления submit_data для GET-запроса"""
        # submit_data возвращает None для GET-запросов, что вызывает ошибку Django
        with self.assertRaises(ValueError):
            self.client.get("/students/submit_data/")

    def test_submit_data_post_request(self):
        """Тест представления submit_data для POST-запроса"""
        response = self.client.post("/students/submit_data/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Данные отправлены!")

    def test_submit_data_function_directly(self):
        """Прямой тест функции submit_data"""
        from django.http import HttpRequest

        # GET запрос
        request = HttpRequest()
        request.method = "GET"
        result = views.submit_data(request)
        self.assertIsNone(result)

        # POST запрос
        request.method = "POST"
        response = views.submit_data(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.content.decode(), "Данные отправлены!")

    def test_show_item_view(self):
        """Тест представления show_item"""
        # Пытается рендерить app/item.html, но шаблона нет
        from django.template import TemplateDoesNotExist

        with self.assertRaises(TemplateDoesNotExist):
            self.client.get("/students/item/123")

    def test_show_item_function_directly(self):
        """Прямой тест функции show_item"""
        from django.http import HttpRequest
        from django.template import TemplateDoesNotExist

        request = HttpRequest()
        # Пытается рендерить несуществующий шаблон app/item.html
        with self.assertRaises(TemplateDoesNotExist):
            views.show_item(request, 123)

    def test_students_list_view(self):
        """Тест представления students_list"""
        # students_list возвращает None, что вызывает ошибку Django
        # Поэтому тест необходимо скипнуть или тестировать отдельно
        #        import unittest
        with self.assertRaises(ValueError):
            self.client.get("/students/list/")

    def test_students_list_function_directly(self):
        """Прямой тест функции students_list"""
        from django.http import HttpRequest

        request = HttpRequest()
        result = views.students_list(request)
        self.assertIsNone(result)

    def test_about_view(self):
        """Тест представления about"""
        response = self.client.get("/students/about/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "О нас")
        self.assertContains(response, "Добро пожаловать на наш сайт!")

    def test_about_function_directly(self):
        """Прямой тест функции about"""
        from django.http import HttpRequest

        request = HttpRequest()
        response = views.about(request)
        self.assertIsNotNone(response)

    def test_contact_get_request(self):
        """Тест представления contact для GET-запроса"""
        response = self.client.get("/students/contact/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Свяжитесь с нами")
        self.assertContains(response, 'form method="post"')
        # CSRF токен рендерится как csrfmiddlewaretoken
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_contact_post_request(self):
        """Тест представления contact для POST-запроса"""
        response = self.client.post(
            "/students/contact/", {"name": "Тестовый пользователь", "message": "Тестовое сообщение"}
        )
        # Контакт в реальном коде обрабатывает POST данные и возвращает HttpResponse
        self.assertEqual(response.status_code, 200)
        # Проверяем, что в ответе есть спасибо с именем пользователя
        self.assertContains(response, "Спасибо, Тестовый пользователь!")
        self.assertContains(response, "Ваше сообщение: Тестовое сообщение получено")

    def test_contact_function_directly(self):
        """Прямой тест функции contact"""
        from django.http import HttpRequest

        # GET запрос
        request = HttpRequest()
        request.method = "GET"
        response = views.contact(request)
        self.assertIsNotNone(response)

        # POST запрос (нужен request.POST для получения данных)
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.post("/students/contact/", {"name": "Тест", "message": "Тест сообщение"})
        response = views.contact(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertIn("Спасибо, Тест!", response.content.decode())


class StudentsUrlsTestCase(TestCase):
    """Тесты для URL-маршрутов приложения students"""

    def test_show_data_url_resolves(self):
        """Тест резолва URL show_data"""
        url = reverse("students:show_data")
        self.assertEqual(url, "/students/show_data/")
        resolver = resolve("/students/show_data/")
        self.assertEqual(resolver.func, views.show_data)
        self.assertEqual(resolver.namespace, "students")
        self.assertEqual(resolver.url_name, "show_data")

    def test_submit_data_url_resolves(self):
        """Тест резолва URL submit_data"""
        url = reverse("students:submit_data")
        self.assertEqual(url, "/students/submit_data/")
        resolver = resolve("/students/submit_data/")
        self.assertEqual(resolver.func, views.submit_data)

    def test_show_item_url_resolves(self):
        """Тест резолва URL show_item"""
        url = reverse("students:show_item", kwargs={"item_id": 123})
        self.assertEqual(url, "/students/item/123")
        resolver = resolve("/students/item/123")
        self.assertEqual(resolver.func, views.show_item)
        self.assertEqual(resolver.kwargs, {"item_id": 123})

    def test_students_list_url_resolves(self):
        """Тест резолва URL list"""
        url = reverse("students:list")
        self.assertEqual(url, "/students/list/")
        resolver = resolve("/students/list/")
        self.assertEqual(resolver.func, views.students_list)

    def test_about_url_resolves(self):
        """Тест резолва URL about"""
        url = reverse("students:about")
        self.assertEqual(url, "/students/about/")
        resolver = resolve("/students/about/")
        self.assertEqual(resolver.func, views.about)

    def test_contact_url_resolves(self):
        """Тест резолва URL contact"""
        url = reverse("students:contact")
        self.assertEqual(url, "/students/contact/")
        resolver = resolve("/students/contact/")
        self.assertEqual(resolver.func, views.contact)


class StudentsModelsTestCase(TestCase):
    """Тесты для моделей приложения students"""

    def test_models_import(self):
        """Тест импорта модулей models"""
        from students import models

        # Проверяем, что модуль можно импортировать
        self.assertIsNotNone(models)
        # В пустом файле нет активных импортов, но модуль существует
        self.assertTrue(hasattr(models, "__file__"))


class StudentsAppsTestCase(TestCase):
    """Тесты для конфигурации приложения students"""

    def test_apps_config(self):
        """Тест конфигурации приложения"""
        from students.apps import StudentsConfig

        self.assertEqual(StudentsConfig.default_auto_field, "django.db.models.BigAutoField")
        self.assertEqual(StudentsConfig.name, "students")
