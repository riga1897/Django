# Руководство разработчика

Документация по требованиям к коду, тестированию и workflow разработки Django проекта с marketplace, blog и users.

## 📋 Содержание

1. [Структура проекта](#структура-проекта)
2. [Требования к коду](#требования-к-коду)
3. [Типизация](#типизация)
4. [Тестирование](#тестирование)
5. [Инструменты качества кода](#инструменты-качества-кода)
6. [Workflow разработки](#workflow-разработки)

---

## Структура проекта

### Текущая организация

```
project_root/
├── marketplace/           # Интернет-магазин (каталог продуктов)
│   ├── models.py         # Category, Product
│   ├── views.py          # ProductsListView, ProductDetailView, ProductCreateView
│   ├── forms.py          # ProductForm, ContactForm
│   ├── signals.py        # Удаление фото при удалении продукта
│   ├── tests.py          # Тесты marketplace (models, views, forms, signals)
│   ├── templates/
│   │   └── marketplace/
│   └── management/
│       └── commands/     # add_products, del_all
├── blog/                 # Блог (публикация постов)
│   ├── models.py         # BlogPost
│   ├── views.py          # BlogPostListView, BlogPostDetailView
│   ├── signals.py        # Удаление preview при удалении поста
│   ├── tests.py          # Тесты blog (models, views, signals)
│   └── templates/
│       └── blog/
├── users/                # Управление пользователями
│   ├── models.py         # User (AbstractUser с email-авторизацией)
│   ├── views.py          # UserRegisterView, UserLoginView, ProfileUpdateView
│   ├── forms.py          # CustomUserCreationForm, CustomAuthenticationForm
│   ├── tests.py          # Тесты users (models, views, forms)
│   └── templates/
│       └── users/
├── config/               # Настройки Django
│   ├── settings.py       # AUTH_USER_MODEL, DATABASE, EMAIL_BACKEND
│   ├── urls.py
│   └── wsgi.py
├── static/               # Статические файлы (Bootstrap 5, custom CSS)
├── media/                # Загруженные файлы пользователей
├── docs/                 # Документация проекта
├── manage.py
├── pyproject.toml        # Poetry зависимости + конфигурация линтеров
├── mypy.ini              # Настройки mypy + django-stubs
└── .gitignore
```

**Примечание**: В будущем можно вынести тесты в отдельную директорию `tests/` для лучшей организации (см. раздел [Тестирование](#тестирование)).

### Ключевые компоненты

#### Marketplace (Интернет-магазин)
**Назначение**: Каталог товаров с категориями, CRUD операциями, валидацией форм

**Модели**:
- `Category` - категории товаров (название, описание)
- `Product` - товары (название, описание, фото, цена, категория)

**Особенности**:
- Защита страниц создания/редактирования через `ModalLoginRequiredMixin`
- Публичный доступ к списку и деталям продуктов
- Валидация форм (запрещенные слова, проверка цены)
- Автоматическое удаление фото через signals

#### Blog (Блог)
**Назначение**: Публикация постов с draft/published статусами

**Модели**:
- `BlogPost` - посты (заголовок, контент, preview, статус публикации, счетчик просмотров)

**Особенности**:
- Draft/Published статусы
- Атомарный счетчик просмотров с `F()` expressions
- Защита создания/редактирования через `ModalLoginRequiredMixin`

#### Users (Пользователи)
**Назначение**: Email-based аутентификация, профили пользователей

**Модели**:
- `User(AbstractUser)` - кастомная модель с email как USERNAME_FIELD
- Дополнительные поля: avatar, phone, country

**Особенности**:
- Модальные окна для login/register (Bootstrap 5)
- Автоматический вход после регистрации
- Welcome email через console backend
- Редактирование профиля

---

## Требования к коду

### 1. Принципы архитектуры

#### Class-Based Views (CBV)
**ОБЯЗАТЕЛЬНО**: Используем CBV для consistency

```python
# ✅ ПРАВИЛЬНО - CBV с миксинами
class ProductCreateView(ModalLoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "marketplace/product_form.html"
    success_url = reverse_lazy("marketplace:products_list")
```

#### Signals для побочных эффектов
**Используем signals** для автоматической очистки файлов:

```python
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

@receiver(post_delete, sender=Product)
def delete_product_photo_on_delete(_sender, instance, **_kwargs):
    """Удаляет файл фото при удалении продукта"""
    if instance.photo:
        instance.photo.delete(save=False)
```

#### DRY (Don't Repeat Yourself)
- Переиспользование базовых шаблонов (`marketplace/base.html`)
- Модальные окна auth в base template
- Миксин `ModalLoginRequiredMixin` для защиты страниц
- Generic form field template

### 2. Валидация данных

#### Валидация на уровне форм

```python
# marketplace/forms.py
FORBIDDEN_WORDS = [
    "казино", "криптовалюта", "крипта", "биржа", 
    "дешево", "бесплатно", "обман", "полиция", "радар"
]

class ProductForm(forms.ModelForm):
    def clean_name(self) -> str:
        name = self.cleaned_data.get("name", "")
        name_lower = name.lower()
        
        for word in FORBIDDEN_WORDS:
            if word in name_lower:
                raise ValidationError(f'Название не может содержать запрещенное слово: "{word}"')
        return name
    
    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price and price < 0:
            raise ValidationError("Цена не может быть отрицательной")
        return price
```

#### Валидация на уровне модели

```python
class Product(models.Model):
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )
```

### 3. Безопасность

#### Защита от open redirect
```python
from django.utils.http import url_has_allowed_host_and_scheme

if not url_has_allowed_host_and_scheme(
    url=next_url,
    allowed_hosts={self.request.get_host()},
    require_https=self.request.is_secure(),
):
    next_url = "/"
```

#### CSRF Protection
Все формы защищены через `{% csrf_token %}`

#### Безопасные redirect параметры
```python
from urllib.parse import urlencode

query_params = {"show_login_modal": "1"}
if next_url:
    query_params["next"] = next_url
return redirect(f"/?{urlencode(query_params)}")
```

---

## Типизация

### ⚠️ ОБЯЗАТЕЛЬНОЕ требование: mypy 0 ошибок

**Проект ОБЯЗАН проходить проверку mypy без ошибок!**

```bash
# Проверка типизации (должна показывать 0 ошибок)
poetry run mypy . --config-file=mypy.ini
# Expected: Success: no issues found in 47 source files
```

### Конфигурация mypy.ini

```ini
[mypy]
plugins = mypy_django_plugin.main

[mypy.plugins.django-stubs]
django_settings_module = config.settings

strict_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_return_any = False
warn_unreachable = True
ignore_missing_imports = True

[mypy-*.migrations.*]
ignore_errors = True
```

### Типизация моделей Django

#### ⚠️ Полная типизация полей моделей

**ОБЯЗАТЕЛЬНО**: Все поля моделей должны иметь type annotations:

```python
# ✅ ПРАВИЛЬНО - явная типизация
class User(AbstractUser):
    email: models.EmailField = models.EmailField(
        verbose_name="Email адрес",
        unique=True
    )
    
    avatar: models.ImageField = models.ImageField(
        upload_to="users/avatars/%Y/%m/%d/",
        blank=True,
        null=True
    )
    
    phone: models.CharField = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []
    
    objects: ClassVar[UserManager] = UserManager()

# ❌ НЕПРАВИЛЬНО - нет аннотаций
class User(AbstractUser):
    email = models.EmailField(unique=True)  # Нет типа!
    avatar = models.ImageField(...)  # Нет типа!
```

### Типизация views

```python
from django.views.generic import ListView

class ProductsListView(ListView):
    """Список всех продуктов"""
    model = Product
    template_name = "marketplace/products_list.html"
    context_object_name = "products"
```

### Типизация форм

```python
from decimal import Decimal
from typing import Any
from django.core.files.uploadedfile import UploadedFile

class ProductForm(forms.ModelForm):
    def clean_price(self) -> Decimal | None:
        """Валидация цены"""
        price = self.cleaned_data.get("price")
        if price and price < 0:
            raise ValidationError("Цена не может быть отрицательной")
        return price
    
    def clean_photo(self) -> UploadedFile | None:
        """Валидация фото"""
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise ValidationError("Размер файла не должен превышать 5 МБ")
        return photo
```

### Типизация signals

```python
from typing import Any
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Product)
def delete_product_photo_on_delete(
    _sender: type[Product],  # Начинается с _ т.к. не используется
    instance: Product,
    **_kwargs: Any  # **_kwargs вместо **kwargs
) -> None:
    """Удаляет файл фото при удалении продукта"""
    if instance.photo:
        instance.photo.delete(save=False)
```

### Целевые type: ignore директивы

**Используйте только целевые type: ignore** для реальных ограничений Django:

```python
# ✅ ПРАВИЛЬНО - целевой ignore
class Meta:  # type: ignore[misc]
    verbose_name = "Пользователь"

# ✅ ПРАВИЛЬНО - целевой ignore для CBV generics
class ProductsListView(ListView):  # type: ignore[type-arg]
    model = Product

# ✅ ПРАВИЛЬНО - ignore для Django ORM magic
user.set_password(password)  # type: ignore[attr-defined]

# ❌ НЕПРАВИЛЬНО - слишком широкий ignore
def some_function():  # type: ignore
    pass  # Игнорирует ВСЕ ошибки!
```

### TYPE_CHECKING для forward references

```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from marketplace.models import Product

class ProductManager(models.Manager):
    def create_product(self, **kwargs: Any) -> "Product":
        """Product в кавычках - forward reference"""
        pass
```

---

## Тестирование

### Фреймворк: pytest-django

**Используем pytest** вместо Django unittest:

```bash
# Установка
poetry add --group tests pytest pytest-django pytest-cov pytest-mock

# Запуск тестов
poetry run pytest

# С покрытием кода
poetry run pytest --cov=marketplace --cov=blog --cov=users --cov-report=html

# Быстрые тесты с переиспользованием БД
poetry run pytest --reuse-db
```

### Структура тестов

**Текущая структура**: Тесты находятся внутри каждого Django приложения

```
marketplace/
└── tests.py           # Все тесты marketplace (models, views, forms, signals)

blog/
└── tests.py           # Все тесты blog (models, views, signals)

users/
└── tests.py           # Все тесты users (models, views, forms)
```

**Рекомендуемая структура** (для роста проекта):

```
tests/
├── marketplace/
│   ├── __init__.py
│   ├── test_models.py       # Тесты Category, Product моделей
│   ├── test_views.py        # Тесты ProductsListView, ProductCreateView
│   ├── test_forms.py        # Тесты ProductForm валидации
│   └── test_signals.py      # Тесты удаления фото
├── blog/
│   ├── test_models.py       # Тесты BlogPost
│   ├── test_views.py        # Тесты BlogPostListView
│   └── test_signals.py      # Тесты удаления preview
├── users/
│   ├── test_models.py       # Тесты User модели
│   ├── test_views.py        # Тесты регистрации, логина
│   └── test_forms.py        # Тесты форм авторизации
└── conftest.py              # Общие фикстуры
```

### Примеры тестов

#### Тесты моделей

```python
import pytest
from marketplace.models import Category, Product

@pytest.mark.django_db
def test_product_creation():
    """Тест создания продукта"""
    category = Category.objects.create(
        name="Электроника",
        description="Электронные товары"
    )
    product = Product.objects.create(
        name="Смартфон",
        description="Новый смартфон",
        price=50000,
        category=category
    )
    
    assert product.name == "Смартфон"
    assert product.price == 50000
    assert product.category == category
    assert str(product) == "Смартфон"

@pytest.mark.django_db
def test_product_str_method():
    """Тест строкового представления"""
    category = Category.objects.create(name="Тест")
    product = Product.objects.create(
        name="Тестовый товар",
        category=category,
        price=100
    )
    assert str(product) == "Тестовый товар"
```

#### Тесты форм

```python
import pytest
from marketplace.forms import ProductForm
from marketplace.models import Category

@pytest.mark.django_db
def test_product_form_valid():
    """Тест валидной формы продукта"""
    category = Category.objects.create(name="Электроника")
    form_data = {
        "name": "Ноутбук",
        "description": "Мощный ноутбук",
        "price": 75000,
        "category": category.id
    }
    form = ProductForm(data=form_data)
    assert form.is_valid()

@pytest.mark.django_db
@pytest.mark.parametrize("forbidden_word", [
    "казино", "криптовалюта", "крипта", "биржа",
    "дешево", "бесплатно", "обман", "полиция", "радар"
])
def test_product_form_forbidden_words(forbidden_word):
    """Тест валидации запрещенных слов"""
    category = Category.objects.create(name="Тест")
    form_data = {
        "name": f"Товар {forbidden_word} онлайн",  # Запрещенное слово
        "description": "Описание",
        "price": 1000,
        "category": category.id
    }
    form = ProductForm(data=form_data)
    assert not form.is_valid()
    assert forbidden_word in str(form.errors).lower()

@pytest.mark.django_db
def test_product_form_negative_price():
    """Тест валидации отрицательной цены"""
    category = Category.objects.create(name="Тест")
    form_data = {
        "name": "Товар",
        "description": "Описание",
        "price": -100,  # Отрицательная цена
        "category": category.id
    }
    form = ProductForm(data=form_data)
    assert not form.is_valid()
    assert "price" in form.errors
```

#### Тесты views

```python
import pytest
from django.urls import reverse
from django.test import Client
from users.models import User

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user():
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123"
    )

@pytest.mark.django_db
def test_products_list_view_public(client):
    """Тест публичного доступа к списку продуктов"""
    url = reverse("marketplace:products_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "products" in response.context

@pytest.mark.django_db
def test_product_create_requires_login(client):
    """Тест защиты страницы создания продукта"""
    url = reverse("marketplace:product_create")
    response = client.get(url)
    # Должен редиректить на главную с параметром модалки
    assert response.status_code == 302
    assert "show_login_modal" in response.url

@pytest.mark.django_db
def test_product_create_authenticated(client, user):
    """Тест создания продукта авторизованным пользователем"""
    client.force_login(user)
    url = reverse("marketplace:product_create")
    response = client.get(url)
    assert response.status_code == 200
```

#### Тесты signals

```python
import pytest
from unittest.mock import Mock, patch
from marketplace.models import Product, Category

@pytest.mark.django_db
def test_product_photo_deleted_on_product_delete():
    """Тест удаления фото при удалении продукта"""
    category = Category.objects.create(name="Тест")
    product = Product.objects.create(
        name="Товар",
        category=category,
        price=1000
    )
    
    # Мокируем фото
    mock_photo = Mock()
    product.photo = mock_photo
    
    # Удаляем продукт
    product.delete()
    
    # Проверяем что photo.delete() был вызван
    mock_photo.delete.assert_called_once_with(save=False)
```

### Фикстуры для переиспользования

```python
# tests/conftest.py
import pytest
from users.models import User
from marketplace.models import Category

@pytest.fixture
def user():
    """Обычный пользователь"""
    return User.objects.create_user(
        email="user@example.com",
        password="userpass123"
    )

@pytest.fixture
def admin_user():
    """Администратор"""
    return User.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123"
    )

@pytest.fixture
def category():
    """Тестовая категория"""
    return Category.objects.create(
        name="Электроника",
        description="Электронные товары"
    )
```

### Покрытие кода

**Целевое покрытие**: 80%+ для критического функционала

```bash
# Генерация HTML отчета
poetry run pytest --cov=marketplace --cov=blog --cov=users \
    --cov-report=html \
    --cov-report=term-missing

# Открыть отчет
open htmlcov/index.html
```

---

## Инструменты качества кода

### Установленные инструменты

- **mypy** - проверка типов (django-stubs plugin)
- **ruff** - быстрый линтер (заменяет flake8)
- **black** - автоформатирование
- **isort** - сортировка импортов
- **pytest** - тестирование

### Конфигурация

#### pyproject.toml

```toml
[tool.ruff]
line-length = 119
preview = true
exclude = [
    ".venv",
    "venv",
    ".local",
    "migrations",
    "__pycache__",
    ".git",
    "*.egg-info",
]

[tool.ruff.lint]
select = ["B", "E", "F", "I", "C90", "UP", "SIM"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.black]
line-length = 119

[tool.isort]
line_length = 119
profile = "black"
```

### Команды проверки

```bash
# Проверка типов
poetry run mypy . --config-file=mypy.ini

# Линтер
poetry run ruff check .

# Автоформатирование
poetry run black .

# Сортировка импортов
poetry run isort .

# Все проверки разом
poetry run mypy . && poetry run ruff check . && poetry run pytest
```

---

## Workflow разработки

### Процесс добавления новой функции

```bash
# 1. Создать ветку
git checkout -b feature/new-feature

# 2. Написать тесты (TDD подход)
# tests/marketplace/test_new_feature.py

# 3. Запустить тесты (они должны упасть - RED)
poetry run pytest tests/marketplace/test_new_feature.py

# 4. Написать код для прохождения тестов (GREEN)
# marketplace/views.py или models.py

# 5. Запустить тесты снова (они должны пройти)
poetry run pytest tests/marketplace/test_new_feature.py

# 6. Рефакторинг кода (REFACTOR)
poetry run black .
poetry run isort .

# 7. Финальная проверка
poetry run mypy .
poetry run ruff check .
poetry run pytest

# 8. Коммит и push
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### Checklist перед коммитом

- [ ] Все тесты проходят: `poetry run pytest`
- [ ] mypy без ошибок: `poetry run mypy .`
- [ ] ruff без ошибок: `poetry run ruff check .`
- [ ] Код отформатирован: `poetry run black .`
- [ ] Импорты отсортированы: `poetry run isort .`
- [ ] Миграции созданы (если изменялись модели)
- [ ] Документация обновлена (если нужно)

### Pull Request

**Структура PR**:

```markdown
## Описание
Краткое описание изменений

## Тип изменений
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Проверка
- [ ] Тесты проходят
- [ ] mypy 0 ошибок
- [ ] ruff 0 ошибок
- [ ] Документация обновлена

## Скриншоты (если UI изменения)
```

---

## Дополнительные материалы

### Полезные команды Django

```bash
# Создание миграций
poetry run python manage.py makemigrations

# Применение миграций
poetry run python manage.py migrate

# Создание суперпользователя
poetry run python manage.py createsuperuser

# Запуск сервера разработки
poetry run python manage.py runserver 0.0.0.0:5000

# Django shell
poetry run python manage.py shell

# Проверка проекта
poetry run python manage.py check
```

### Управление зависимостями

```bash
# Добавить зависимость
poetry add package-name

# Добавить dev зависимость
poetry add --group lint package-name

# Обновить зависимости
poetry update

# Показать установленные пакеты
poetry show
```

---

## Заключение

Следование этому руководству обеспечивает:
- ✅ Высокое качество кода (mypy, ruff, black)
- ✅ Надежность (покрытие тестами)
- ✅ Безопасность (валидация, CSRF, safe redirects)
- ✅ Поддерживаемость (типизация, документация)
- ✅ Консистентность (CBV, signals, DRY)

**Главное правило**: Код без тестов и типизации не мерджится!
