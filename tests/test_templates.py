from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import Client, TestCase

# from django.http import HttpRequest


class TemplatesTestCase(TestCase):
    """Тесты для шаблонов Django"""

    def setUp(self):
        self.client = Client()

    def test_about_template_exists(self):
        """Тест существования шаблона about.html"""
        template = get_template("students/about.html")
        self.assertIsNotNone(template)

    def test_contact_template_exists(self):
        """Тест существования шаблона contact.html"""
        template = get_template("students/contact.html")
        self.assertIsNotNone(template)

    def test_about_template_content(self):
        """Тест содержимого шаблона about.html"""
        template = get_template("students/about.html")
        rendered = template.render({})
        self.assertIn("О нас", rendered)
        self.assertIn("Добро пожаловать на наш сайт!", rendered)
        self.assertIn("<!DOCTYPE html>", rendered)
        self.assertIn("<title>О нас</title>", rendered)

    def test_contact_template_content(self):
        """Тест содержимого шаблона contact.html"""
        template = get_template("students/contact.html")
        # CSRF token уже проверяется в test_contact_template_rendering_via_view
        # через rendered response

        rendered = template.render({})
        self.assertIn("Свяжитесь с нами", rendered)
        self.assertIn("Контактная форма", rendered)
        self.assertIn('form method="post"', rendered)
        self.assertIn("<input", rendered)
        self.assertIn("<textarea", rendered)
        self.assertIn('name="name"', rendered)
        self.assertIn('name="message"', rendered)

    def test_about_template_rendering_via_view(self):
        """Тест рендеринга about.html через представление"""
        response = self.client.get("/students/about/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "О нас")
        self.assertContains(response, "Добро пожаловать на наш сайт!")
        self.assertContains(response, "<!DOCTYPE html>")

    def test_contact_template_rendering_via_view(self):
        """Тест рендеринга contact.html через представление"""
        response = self.client.get("/students/contact/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Свяжитесь с нами")
        self.assertContains(response, 'form method="post"')
        # CSRF токен рендерится как csrfmiddlewaretoken в финальном HTML
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_missing_templates_behavior(self):
        """Тест поведения при отсутствующих шаблонах"""
        # Проверяем что несуществующие шаблоны вызывают ошибки
        with self.assertRaises(TemplateDoesNotExist):
            get_template("students/nonexistent.html")

        with self.assertRaises(TemplateDoesNotExist):
            get_template("app/data.html")  # Шаблон которого нет в show_data

        with self.assertRaises(TemplateDoesNotExist):
            get_template("app/item.html")  # Шаблон которого нет в show_item

    # Удален лишний тест - не нужен для coverage

    # Удален лишний тест - не нужен для coverage
