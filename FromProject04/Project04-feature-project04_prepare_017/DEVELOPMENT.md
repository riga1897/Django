# Руководство разработчика

Документация по требованиям к коду, тестированию и workflow разработки проекта.

## 📋 Содержание

1. [TDD Workflow (Test-Driven Development)](#tdd-workflow-test-driven-development)
2. [Требования к коду](#требования-к-коду)
3. [Требования к тестам](#требования-к-тестам)
4. [Инструменты качества кода](#инструменты-качества-кода)
5. [Валидация данных](#валидация-данных)
6. [Workflow разработки](#workflow-разработки)
7. [Примеры использования](#примеры-использования)

---

## TDD Workflow (Test-Driven Development)

### ⚠️ ОБЯЗАТЕЛЬНЫЙ порядок разработки

**В этом проекте мы следуем строгому TDD подходу!**

#### Цикл RED-GREEN-REFACTOR

```
1. 🔴 RED: Пишем тест (он падает - функционала еще нет)
         ↓
2. 🟢 GREEN: Пишем минимальный код, чтобы тест прошел
         ↓
3. 🔵 REFACTOR: Улучшаем код, тесты остаются зелеными
         ↓
    Повторяем для следующей функции
```

#### Золотое правило

**НЕТ КОДА БЕЗ ТЕСТОВ!**

Любой функциональный код должен быть покрыт тестами **ДО** или **ОДНОВРЕМЕННО** с его написанием.

#### Порядок разработки модулей

**1. Core (apps/core/)** - Фундамент системы
```bash
# Пример: Разработка BaseModel
pytest tests/core/test_models.py::test_base_model_soft_delete  # RED
# → Пишем метод soft_delete() в BaseModel
pytest tests/core/test_models.py::test_base_model_soft_delete  # GREEN
# → Рефакторим если нужно
```

Порядок:
- ✅ BaseModel → тесты → реализация
- ✅ OwnedModel → тесты → реализация
- ✅ BaseService → тесты → реализация
- ✅ Mixins → тесты → реализация
- ✅ Permissions → тесты → реализация
- ✅ Validators → тесты → реализация

**2. Users (apps/users/)** - Управление пользователями
```bash
# Пример: Разработка User модели
pytest tests/users/test_models.py::test_user_creation  # RED
# → Создаем User модель
pytest tests/users/test_models.py::test_user_creation  # GREEN
```

**3. Mailings (apps/mailings/)** - Бизнес-логика рассылок
```bash
# Аналогично для Recipient, Message, Mailing, Attempt
pytest tests/mailings/test_models.py::test_recipient_creation  # RED → GREEN
```

#### Пример TDD сессии

```bash
# 1. Пишем тест
$ cat > tests/core/test_models.py
@pytest.mark.django_db
def test_base_model_has_created_at():
    obj = SomeModel.objects.create(name="Test")
    assert obj.created_at is not None
    assert isinstance(obj.created_at, datetime)

# 2. Запускаем - должен упасть (RED)
$ pytest tests/core/test_models.py::test_base_model_has_created_at
FAILED - AttributeError: 'SomeModel' object has no attribute 'created_at'

# 3. Добавляем поле в BaseModel
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

# 4. Запускаем - должен пройти (GREEN)
$ pytest tests/core/test_models.py::test_base_model_has_created_at
PASSED

# 5. Рефакторим если нужно, тесты продолжают проходить
```

#### Проверка покрытия

После каждого модуля проверяем 100% покрытие:

```bash
# Проверка покрытия core
pytest --cov=apps/core --cov-report=term-missing tests/core/

# Должно быть 100%
apps/core/models.py      100%
apps/core/services.py    100%
apps/core/mixins.py      100%
...
```

#### Что делать если тест не падает сразу?

Если написали тест и он сразу зеленый - **возможно что-то не так!**

- Проверьте, что тестируете новую функциональность
- Убедитесь, что тест действительно проверяет нужное поведение
- Попробуйте специально сломать код - тест должен упасть

---

## Требования к коду

### 1. Структура проекта

```
project_root/
├── apps/                   # Все Django приложения
│   ├── core/              # ЯДРО - неизменяемая основа
│   │   ├── models.py      # BaseModel, OwnedModel
│   │   ├── services.py    # BaseService, BaseCRUDService
│   │   ├── mixins.py      # Переиспользуемые миксины
│   │   ├── permissions.py # Проверка прав доступа
│   │   └── validators.py  # Pydantic валидаторы
│   ├── users/             # Управление пользователями
│   └── mailings/          # Управление рассылками
├── config/                # Настройки Django
├── tests/                 # Все тесты
└── static/                # Статические файлы
```

### 2. Принципы архитектуры

#### ABC классы (Abstract Base Classes)

**ОБЯЗАТЕЛЬНО**: Абстрактные классы НЕ должны содержать реализации!

```python
# ✅ ПРАВИЛЬНО - чистая абстракция
class BaseService(ABC):
    @abstractmethod
    def validate(self, data: dict[str, Any]) -> bool:
        pass

# ❌ НЕПРАВИЛЬНО - содержит реализацию
class BaseService(ABC):
    def __init__(self):
        self.errors = []  # Это реализация!
```

**Решение**: Разделяем на абстракцию и реализацию

```python
class BaseService(ABC):
    """Чистая абстракция"""
    @abstractmethod
    def validate(self, data: dict[str, Any]) -> bool:
        pass

class BaseServiceWithErrors(BaseService):
    """Реализация с обработкой ошибок"""
    def __init__(self):
        self.errors = []
```

#### Композиция вместо наследования

**Используем миксины** для переиспользования кода:

```python
class RecipientService(BaseCRUDService, OwnerFilterMixin, LoggingMixin):
    def __init__(self):
        super().__init__(Recipient)
```

#### Dependency Injection

Сервисы получают зависимости через `__init__`:

```python
class MailingService:
    def __init__(self, email_sender: EmailSender, logger: Logger):
        self.email_sender = email_sender
        self.logger = logger
```

### 3. Типизация кода

#### ⚠️ ОБЯЗАТЕЛЬНОЕ требование: 100% Type Coverage

**Проект ОБЯЗАН поддерживать 100% покрытие типами с нулевыми ошибками mypy!**

```bash
# Проверка типизации (должна показывать 0 ошибок)
poetry run mypy .
# Expected output: Success: no issues found in 51 source files
```

#### Явная типизация всех полей моделей Django

**ОБЯЗАТЕЛЬНО**: Все поля Django моделей должны иметь явные type annotations:

```python
# ✅ ПРАВИЛЬНО - явная типизация
class User(AbstractUser, BaseModel):
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

# ❌ НЕПРАВИЛЬНО - нет типизации
class User(AbstractUser, BaseModel):
    email = models.EmailField(verbose_name="Email адрес")  # Нет аннотации!
    avatar = models.ImageField(upload_to="...")  # Нет аннотации!
```

#### Generic Service Pattern

**ОБЯЗАТЕЛЬНО**: Сервисы должны использовать Generic[T] для правильного вывода типов:

```python
from typing import Generic, TypeVar, Optional
from django.db.models import Model, QuerySet

T = TypeVar("T", bound=Model)

# ✅ ПРАВИЛЬНО - Generic pattern
class BaseCRUDService(Generic[T]):
    """Базовый CRUD сервис с Generic типизацией"""
    
    def __init__(self, model_class: type[T]) -> None:
        self.model_class = model_class
    
    def get_by_id(self, pk: int) -> Optional[T]:
        """Возвращает конкретный тип модели, не Model"""
        return self.model_class.objects.filter(pk=pk).first()
    
    def get_all(self) -> QuerySet[T]:
        """Возвращает типизированный QuerySet"""
        return self.model_class.objects.all()

# Использование в конкретных сервисах
class RecipientService(BaseCRUDService[Recipient]):
    def __init__(self):
        super().__init__(Recipient)
    
    # Методы автоматически возвращают Recipient, не Model!
```

#### Целевые type: ignore директивы

**Используйте только целевые type: ignore** для реальных ограничений Django:

```python
# ✅ ПРАВИЛЬНО - целевой ignore для Django ORM
class RecipientForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recipients"].queryset = (  # type: ignore[attr-defined]
            Recipient.objects.filter(owner=user, is_active=True)
        )

# ✅ ПРАВИЛЬНО - целевой ignore для custom user методов
if not self.request.user.is_manager():  # type: ignore[union-attr]
    queryset = queryset.filter(owner=self.request.user)

# ✅ ПРАВИЛЬНО - целевой ignore для override Django методов
class UserManager(DjangoUserManager):
    def create_user(
        self, 
        email: str, 
        password: Optional[str] = None, 
        **extra_fields: Any
    ) -> "User":  # type: ignore[override]
        pass

# ❌ НЕПРАВИЛЬНО - слишком широкий ignore
def some_function():  # type: ignore
    pass  # Игнорирует ВСЕ типы ошибок!

# ❌ НЕПРАВИЛЬНО - множественные ignore без необходимости
def create_user(...) -> "User":  # type: ignore[name-defined,override]
    # Должен быть только override, а name-defined решается через TYPE_CHECKING
    pass
```

#### TYPE_CHECKING для forward references

**Используйте TYPE_CHECKING** для разрешения circular imports:

```python
from typing import TYPE_CHECKING, Any, Optional
from django.contrib.auth.models import UserManager as DjangoUserManager

# ✅ ПРАВИЛЬНО - импорт только для type checking
if TYPE_CHECKING:
    from apps.users.models import User

class UserManager(DjangoUserManager):
    def create_user(
        self, 
        email: str, 
        password: Optional[str] = None,
        **extra_fields: Any
    ) -> "User":  # type: ignore[override]
        """User в кавычках - forward reference"""
        pass

# ❌ НЕПРАВИЛЬНО - реальный импорт вызовет circular import
from apps.users.models import User  # Ошибка!
```

#### Категории type: ignore директив

Используйте только следующие категории:

| Директива | Когда использовать | Пример |
|-----------|-------------------|---------|
| `[override]` | Django метод с другой сигнатурой | UserManager.create_user() |
| `[attr-defined]` | Django ORM атрибуты | queryset, owner_id, input_formats |
| `[union-attr]` | Custom методы на request.user | is_manager(), is_active |
| `[no-any-return]` | self.model возвращает Any | return user (в Manager) |
| `[assignment]` | reverse_lazy() возвращает _StrPromise | next_page = str(reverse_lazy(...)) |

#### Проверка типизации

**Запускайте mypy регулярно:**

```bash
# Полная проверка проекта
poetry run mypy .

# Проверка конкретного модуля
poetry run mypy apps/core/

# Проверка с подробным выводом
poetry run mypy --show-error-codes apps/

# Должен быть результат:
# Success: no issues found in 51 source files
```

#### Интеграция в CI/CD

```bash
# В pipeline добавьте проверку mypy ПЕРЕД тестами
poetry run mypy .
if [ $? -ne 0 ]; then
    echo "❌ Mypy проверка провалена! Исправьте ошибки типов."
    exit 1
fi

poetry run pytest
```

#### Важно помнить

- ❌ **НЕТ ошибок mypy = НЕТ merge!**
- ✅ Все поля моделей должны быть типизированы
- ✅ Generic[T] pattern для всех базовых сервисов
- ✅ Только целевые type: ignore директивы
- ✅ TYPE_CHECKING для forward references
- ✅ Документируйте причину каждого type: ignore

---

### 4. Отсутствие дублирования (DRY)

- Используем миксины для общего функционала
- Создаем базовые классы для похожих сущностей
- Функции должны делать одну вещь хорошо

### 5. Качество кода

#### flake8

Код **ОБЯЗАТЕЛЬНО** должен проходить проверку flake8 без ошибок:

```bash
poetry run flake8 apps/ config/
```

#### Документация

Все классы, методы и функции **ОБЯЗАТЕЛЬНО** должны быть задокументированы на русском языке:

```python
def create_recipient(email: str, name: str) -> Recipient:
    """
    Создать нового получателя рассылки.
    
    Args:
        email: Email адрес получателя
        name: Полное имя получателя
        
    Returns:
        Созданный объект Recipient
        
    Raises:
        ValidationError: Если email невалидный
    """
    pass
```

---

## Требования к тестам

### 1. Фреймворк

**Используем pytest-django** вместо Django unittest:

```bash
# Запуск тестов
pytest

# Параллельное выполнение (быстрее)
pytest -n auto

# С покрытием кода
pytest --cov=apps --cov-report=html

# С переиспользованием БД (еще быстрее)
pytest --reuse-db -n auto
```

### 2. Стратегия тестирования

**Порядок приоритета** (от ядра к приложениям):

1. **apps/core/** - тесты ядра (100% покрытие)
   - BaseModel, OwnedModel
   - BaseService, BaseCRUDService
   - Миксины (OwnerFilterMixin, LoggingMixin, CacheMixin)
   - Permissions

2. **apps/users/** - тесты users (100% покрытие)
   - Модель User
   - UserService
   - Формы, views

3. **apps/mailings/** - тесты mailings (100% покрытие)
   - Модели (Recipient, Message, Mailing, Attempt)
   - Сервисы
   - Команды management
   - Формы, views

4. **Интеграционные тесты**
   - Полный цикл рассылки
   - Проверка прав доступа (User vs Manager)

### 3. Принципы тестирования

#### Изоляция тестов

Каждый тест независим и не влияет на другие:

```python
@pytest.mark.django_db
def test_create_recipient():
    # Arrange
    data = {"email": "test@example.com", "full_name": "Test User"}
    
    # Act
    recipient = Recipient.objects.create(**data)
    
    # Assert
    assert recipient.email == "test@example.com"
    # БД автоматически откатывается после теста
```

#### Нет дублей в покрытии

Тесты не должны покрывать код более одного раза:

```python
# ✅ ПРАВИЛЬНО - тестируем BaseModel один раз
def test_base_model_soft_delete():
    obj = SomeModel.objects.create(name="Test")
    obj.soft_delete()
    assert obj.is_active == False

# ❌ НЕПРАВИЛЬНО - повторное тестирование того же функционала
def test_recipient_soft_delete():
    recipient = Recipient.objects.create(...)
    recipient.soft_delete()  # Уже протестировано в BaseModel!
```

#### Моки для внешних сервисов

**ОБЯЗАТЕЛЬНО** мокировать:
- `send_mail()` - не отправляем реальные письма
- Внешние API
- Файловую систему (где возможно)

```python
@pytest.mark.django_db
def test_send_mailing(mocker):
    # Мокируем отправку email
    mock_send = mocker.patch('django.core.mail.send_mail')
    
    # Отправляем рассылку
    send_mailing(mailing_id=1)
    
    # Проверяем что send_mail был вызван
    assert mock_send.called
```

#### Параметризация тестов

Используем `@pytest.mark.parametrize` для тестирования множества сценариев:

```python
@pytest.mark.parametrize("email,valid", [
    ("test@example.com", True),
    ("invalid", False),
    ("@example.com", False),
    ("test@", False),
])
def test_email_validation(email, valid):
    result = validate_email(email)
    assert result == valid
```

#### Фикстуры для переиспользования

```python
@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        password="password123"
    )

@pytest.fixture
def manager():
    user = User.objects.create_user(
        email="manager@example.com",
        password="password123"
    )
    user.is_staff = True
    user.save()
    return user

def test_user_permissions(user, manager):
    # Используем фикстуры
    pass
```

### 4. Структура тестов

```
tests/
├── core/
│   ├── test_models.py        # Тесты BaseModel, OwnedModel
│   ├── test_services.py      # Тесты BaseService, BaseCRUDService
│   ├── test_mixins.py        # Тесты миксинов
│   └── test_permissions.py   # Тесты прав доступа
├── users/
│   ├── test_models.py        # Тесты User модели
│   ├── test_services.py      # Тесты UserService
│   └── test_views.py         # Тесты views
├── mailings/
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_views.py
│   └── test_commands.py      # Тесты management команд
└── integration/
    └── test_mailing_flow.py  # Интеграционные тесты
```

### 5. Целевое покрытие

**100% покрытие функционального кода** без избыточных проверок!

```bash
# Проверка покрытия
pytest --cov=apps --cov-report=term-missing

# HTML отчет
pytest --cov=apps --cov-report=html
# Открыть htmlcov/index.html
```

---

## Инструменты качества кода

### 1. Установленные инструменты

- **flake8** - проверка стиля кода
- **black** - автоформатирование
- **isort** - сортировка импортов
- **pre-commit** - автоматические проверки перед коммитом
- **pytest-django** - тестирование
- **pytest-cov** - покрытие кода

### 2. Конфигурационные файлы

#### `.editorconfig`

Настройки редактора (автоматически):
- UTF-8 encoding
- Удаление trailing whitespace
- Пустая строка в конце файла
- 4 пробела для отступов в Python

#### `.flake8`

```ini
[flake8]
max-line-length = 119
max-complexity = 10
ignore = E203, W503, E501
```

#### `pyproject.toml`

Настройки black, isort, pytest:

```toml
[tool.black]
line-length = 119

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
addopts = ["-v", "--reuse-db", "--cov=apps"]
```

### 3. Команды

```bash
# Автоформатирование
poetry run black apps/ config/

# Сортировка импортов
poetry run isort apps/ config/

# Проверка стиля
poetry run flake8 apps/ config/

# Проверка типизации (ОБЯЗАТЕЛЬНО перед коммитом!)
poetry run mypy .

# Запуск всех проверок
poetry run pre-commit run --all-files

# Тесты
poetry run pytest

# Тесты с покрытием
poetry run pytest --cov=apps --cov-report=html
```

---

## Валидация данных

### 1. Django Forms (основной инструмент)

**Используйте Django Forms/ModelForms для:**
- Валидации форм пользователя
- Проверки данных моделей
- Автоматической генерации HTML форм
- Обработки GET/POST запросов

#### Пример Django Form

```python
from django import forms
from .models import Recipient

class RecipientForm(forms.ModelForm):
    """Форма создания получателя"""
    
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
    
    def clean_full_name(self):
        """Кастомная валидация имени"""
        full_name = self.cleaned_data.get('full_name')
        if not full_name or not full_name.strip():
            raise forms.ValidationError("Имя не может быть пустым")
        return full_name.strip()

# Использование в view
def create_recipient(request):
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.owner = request.user
            recipient.save()
            return redirect('success')
    else:
        form = RecipientForm()
    return render(request, 'form.html', {'form': form})
```

### 2. Pydantic (для сложных случаев)

**Используйте Pydantic, когда Django Forms недостаточно:**
- Сложная кросс-полевая валидация
- Интеграция с внешними API
- Валидация настроек (.env файлов) через pydantic-settings
- Сериализация/десериализация сложных структур данных

#### Пример Pydantic валидатора

```python
from pydantic import BaseModel, field_validator, model_validator

class ComplexValidator(BaseModel):
    """Пример сложной валидации с Pydantic"""
    
    email: str
    password: str
    password_confirm: str
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        """Проверка домена через внешний API"""
        # Ваша сложная логика с внешним API
        if not is_valid_domain(v.split('@')[1]):
            raise ValueError('Недопустимый email домен')
        return v
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Кросс-полевая валидация"""
        if self.password != self.password_confirm:
            raise ValueError('Пароли не совпадают')
        return self

# Использование
try:
    validator = ComplexValidator(**data)
    validated_data = validator.model_dump()
except ValidationError as e:
    errors = e.errors()
```

### 3. Когда что использовать?

| Задача | Инструмент | Причина |
|--------|-----------|---------|
| Формы пользователя | Django Forms | Встроенная интеграция с Django |
| CRUD операции | ModelForms | Автоматическая связь с моделями |
| Валидация .env | Pydantic Settings | Специализированный инструмент |
| Сложная бизнес-логика | Pydantic | Мощные возможности валидации |
| API запросы/ответы | Django Forms или Pydantic | В зависимости от сложности |

---

## Workflow разработки

### 1. Создание новой фичи

```bash
# 1. Создаем новую ветку (если используется Git)
git checkout -b feature/new-feature

# 2. Пишем код
# ... редактируем файлы ...

# 3. Автоформатирование
poetry run black apps/ config/
poetry run isort apps/ config/

# 4. Проверка стиля
poetry run flake8 apps/ config/

# 5. Запуск тестов
poetry run pytest

# 6. Проверка покрытия
poetry run pytest --cov=apps --cov-report=term-missing

# 7. Коммит (pre-commit hooks запустятся автоматически)
git add .
git commit -m "Добавлена новая фича"
```

### 2. Перед коммитом

Pre-commit hooks **автоматически** выполнят:
1. Удаление trailing whitespace
2. Проверка YAML/TOML файлов
3. Black форматирование
4. isort сортировка импортов
5. flake8 проверка стиля

Если проверка не пройдена - коммит будет отклонен!

### 3. Запуск тестов

```bash
# Все тесты
pytest

# Только тесты core
pytest tests/core/

# Конкретный файл
pytest tests/core/test_models.py

# Конкретный тест
pytest tests/core/test_models.py::test_base_model_soft_delete

# Параллельно (быстрее)
pytest -n auto

# С переиспользованием БД (еще быстрее)
pytest --reuse-db -n auto

# С покрытием
pytest --cov=apps --cov-report=html
```

---

## Примеры использования

### Пример 1: Создание нового сервиса

```python
# apps/mailings/services.py
from apps.core.services import BaseCRUDService
from apps.core.mixins import LoggingMixin, CacheMixin
from apps.mailings.models import Recipient

class RecipientService(BaseCRUDService, LoggingMixin, CacheMixin):
    """Сервис для управления получателями рассылок"""
    
    def __init__(self):
        super().__init__(Recipient)
    
    def validate(self, data: dict) -> bool:
        """Кастомная валидация получателя"""
        if not super().validate(data):
            return False
            
        # Дополнительные проверки
        if not data.get('email'):
            self.add_error("Email обязателен")
            return False
            
        return True
```

### Пример 2: Использование сервиса во view

```python
# apps/mailings/views.py
from django.views.generic import CreateView
from apps.mailings.services import RecipientService

class RecipientCreateView(CreateView):
    def form_valid(self, form):
        service = RecipientService()
        
        data = form.cleaned_data
        recipient = service.create(data, owner=self.request.user)
        
        if recipient:
            return redirect('success')
        else:
            # Показываем ошибки
            for error in service.get_errors():
                form.add_error(None, error)
            return self.form_invalid(form)
```

### Пример 3: Тестирование сервиса

```python
# tests/mailings/test_services.py
import pytest
from apps.mailings.services import RecipientService
from apps.users.models import User

@pytest.fixture
def user(db):
    return User.objects.create_user(email="test@example.com")

@pytest.fixture
def service():
    return RecipientService()

@pytest.mark.django_db
class TestRecipientService:
    def test_create_recipient(self, service, user):
        # Arrange
        data = {
            "email": "recipient@example.com",
            "full_name": "Test Recipient"
        }
        
        # Act
        recipient = service.create(data, owner=user)
        
        # Assert
        assert recipient is not None
        assert recipient.email == "recipient@example.com"
        assert recipient.owner == user
    
    def test_create_without_email_fails(self, service, user):
        # Arrange
        data = {"full_name": "Test"}
        
        # Act
        recipient = service.create(data, owner=user)
        
        # Assert
        assert recipient is None
        assert service.has_errors()
        assert "Email обязателен" in service.get_errors()
```

---

## Чек-лист перед коммитом

- [ ] Код отформатирован (black, isort)
- [ ] Нет ошибок flake8
- [ ] Все новые функции/классы задокументированы
- [ ] Написаны тесты для нового кода
- [ ] Все тесты проходят (`pytest`)
- [ ] Покрытие кода не уменьшилось
- [ ] Pre-commit hooks проходят успешно

---

## Полезные ссылки

- [pytest-django документация](https://pytest-django.readthedocs.io/)
- [Pydantic документация](https://docs.pydantic.dev/)
- [Black документация](https://black.readthedocs.io/)
- [flake8 правила](https://flake8.pycqa.org/en/latest/user/error-codes.html)
