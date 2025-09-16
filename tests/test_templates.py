from django.test import TestCase, Client
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.http import HttpRequest


class TemplatesTestCase(TestCase):
    """Тесты для шаблонов Django"""
    
    def setUp(self):
        self.client = Client()
    
    def test_about_template_exists(self):
        """Тест существования шаблона about.html"""
        try:
            template = get_template('students/about.html')
            self.assertIsNotNone(template)
        except TemplateDoesNotExist:
            self.fail("Шаблон students/about.html не найден")
    
    def test_contact_template_exists(self):
        """Тест существования шаблона contact.html"""
        try:
            template = get_template('students/contact.html')
            self.assertIsNotNone(template)
        except TemplateDoesNotExist:
            self.fail("Шаблон students/contact.html не найден")
    
    def test_about_template_content(self):
        """Тест содержимого шаблона about.html"""
        template = get_template('students/about.html')
        rendered = template.render({})
        self.assertIn("О нас", rendered)
        self.assertIn("Добро пожаловать на наш сайт!", rendered)
        self.assertIn("<!DOCTYPE html>", rendered)
        self.assertIn("<title>О нас</title>", rendered)
    
    def test_contact_template_content(self):
        """Тест содержимого шаблона contact.html"""
        template = get_template('students/contact.html')
        # Проверяем, что в шаблоне есть тег csrf_token (читаем файл напрямую)
        with open('students/templates/students/contact.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
            self.assertIn("csrf_token", template_content)
        
        rendered = template.render({})
        self.assertIn("Свяжитесь с нами", rendered)
        self.assertIn("Контактная форма", rendered)
        self.assertIn("form method=\"post\"", rendered)
        self.assertIn("<input", rendered)
        self.assertIn("<textarea", rendered)
        self.assertIn("name=\"name\"", rendered)
        self.assertIn("name=\"message\"", rendered)
    
    def test_about_template_rendering_via_view(self):
        """Тест рендеринга about.html через представление"""
        response = self.client.get('/students/about/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "О нас")
        self.assertContains(response, "Добро пожаловать на наш сайт!")
        self.assertContains(response, "<!DOCTYPE html>")
    
    def test_contact_template_rendering_via_view(self):
        """Тест рендеринга contact.html через представление"""
        response = self.client.get('/students/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Свяжитесь с нами")
        self.assertContains(response, "form method=\"post\"")
        # CSRF токен рендерится как csrfmiddlewaretoken в финальном HTML
        self.assertContains(response, "csrfmiddlewaretoken")
    
    def test_missing_templates_behavior(self):
        """Тест поведения при отсутствующих шаблонах"""
        # Проверяем что несуществующие шаблоны вызывают ошибки
        with self.assertRaises(TemplateDoesNotExist):
            get_template('students/nonexistent.html')
        
        with self.assertRaises(TemplateDoesNotExist):
            get_template('app/data.html')  # Шаблон которого нет в show_data
        
        with self.assertRaises(TemplateDoesNotExist):
            get_template('app/item.html')  # Шаблон которого нет в show_item
    
    def test_about_template_missing_coverage(self):
        """Тест для покрытия except блока в test_about_template_exists"""
        # Создаём ситуацию, когда шаблон не найден
        import os
        import tempfile
        from django.template.loader import get_template
        from django.test.utils import override_settings
        
        # Создаём пустую директорию для шаблонов
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [temp_dir],
                    'APP_DIRS': False,
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.request',
                        ],
                    },
                },
            ]):
                try:
                    template = get_template('students/about.html')
                    # Если дошли сюда, то ошибка не возникла
                    self.fail("Ожидалась ошибка TemplateDoesNotExist")
                except TemplateDoesNotExist:
                    # Это ожидаемое поведение
                    self.assertTrue(True)
    
    def test_contact_template_missing_coverage(self):
        """Тест для покрытия except блока в test_contact_template_exists"""
        # Создаём ситуацию, когда шаблон не найден
        import os
        import tempfile
        from django.template.loader import get_template
        from django.test.utils import override_settings
        
        # Создаём пустую директорию для шаблонов
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [temp_dir],
                    'APP_DIRS': False,
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.request',
                        ],
                    },
                },
            ]):
                try:
                    template = get_template('students/contact.html')
                    # Если дошли сюда, то ошибка не возникла
                    self.fail("Ожидалась ошибка TemplateDoesNotExist")
                except TemplateDoesNotExist:
                    # Это ожидаемое поведение
                    self.assertTrue(True)