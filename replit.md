# Overview

This is a Django-based web application with three main components: a marketplace (e-commerce product catalog), a blog system, and user management with email-based authentication. The application uses Bootstrap 5 for styling and includes custom CSS for visual enhancements. The project follows Django best practices with proper separation of concerns across apps, aiming to provide a robust platform for e-commerce and content publishing.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture

**Framework**: Django 5.2.7 with Python 3.x

**Project Structure**: Multi-app Django project with modular design for `marketplace`, `blog`, `users`, and `config` (project-level settings).

**Design Patterns**:
- Class-Based Views (CBVs) for CRUD operations.
- Django signals for automatic cleanup of uploaded files.
- Custom mixins (`ModalLoginRequiredMixin`) for modal-based login authentication.
- Custom managers (`UserManager`) for email-based user creation.

## Data Architecture

**Database**: PostgreSQL, configured for environment-based connection strings.

**Key Models**: `Product`, `Category`, `BlogPost`, and a custom `User` model extending `AbstractUser` with email as the username field.

**Model Relationships**: `Product` to `Category` (ForeignKey with CASCADE delete). Signal handlers manage file cleanup for `Product.photo` and `BlogPost.preview`.

## Authentication & Authorization

**Authentication Strategy**: Email-based authentication using a custom `User` model and `UserManager`.

**Access Control**: Django's `LoginRequiredMixin` extended for modal-based login. Access control includes conditional field display and queryset filtering based on user roles (owner, moderator, staff).

## Frontend Architecture

**Template System**: Django templates with Bootstrap 5, utilizing template inheritance and custom template tags.

**Static Assets**: Bootstrap 5.3.8 and custom CSS with CSS variables for a consistent gradient-based visual design system.

**UI Patterns**: Modal-based authentication, responsive design, and gradient-based color coding for various actions and states.

## File Management

**Strategy**: Automatic cleanup via Django `pre_save` and `post_delete` signals for uploaded files (product photos, blog previews).

## Form Validation

**Custom Validation Rules**: Include forbidden words filtering, non-negative price validation, file size limits, and email uniqueness/normalization.

## URL Routing

**Structure**: Namespaced URL patterns per app (`marketplace:`, `blog:`, `users:`) and an admin interface at `/admin/`.

## Permissions and Moderation Framework

**Models**: `Product` and `BlogPost` include `owner` (ForeignKey to User) and `is_published` (BooleanField).

**Permission Groups**: "Модератор продуктов" (Product Moderators) and "Контент-менеджер" (Content Managers) with specific permissions like `can_unpublish_product` and `can_unpublish_post`.

**Access Control Logic**:
- **Create**: Auto-assigns current user as owner.
- **Update**: Owner-only for content editing, moderators can reassign ownership.
- **Delete**: Owner OR moderator.
- **Toggle Publication**: Owner OR moderator can toggle `is_published` status.
- **View Filtering**: Unauthenticated users see only published content; authenticated staff/moderators see all; owners see their own unpublished content.
- **Owner Deletion**: Content is preserved by reassigning to a system user (`deleted@system.user`) on owner deletion.

# External Dependencies

## Core Framework
- **Django 5.2.7** - Web framework
- **Python 3.x** - Runtime environment

## Database
- **PostgreSQL** - Primary database
- **dj-database-url** - Database URL parsing

## Environment Management
- **python-dotenv** - Environment variable management

## Email
- Django's built-in email backend - For user registration and password resets

## Media & Static Files
- Django's built-in static files handling
- ImageField for image uploads

## Frontend Libraries
- **Bootstrap 5.3.8** - CSS framework and JavaScript components

## Development Tools
- **mypy** - Static type checking
- **ruff** - Python linter
- **black** - Code formatter
- **isort** - Import sorter
- **pytest-django** - Testing framework

# Documentation

**Developer Guide**: See `docs/DEVELOPMENT.md` for:
- Code requirements and best practices
- Type annotation guidelines (mypy configuration)
- Testing strategy with pytest-django
- Quality tools setup (ruff, black, isort)
- Workflow and deployment processes
- Real examples from marketplace, blog, and users apps

# Recent Changes

## October 18, 2025

### Owner Visibility and Type Safety (Latest)
- **Скрыта информация о владельце для неавторизованных пользователей**:
  - В `product_detail.html` и `blogpost_detail.html` блок с владельцем обернут в `{% if user.is_authenticated %}`
  - Неавторизованные пользователи больше не видят email владельца товара/поста
  - Авторизованные пользователи видят владельца как раньше (с сохранением логики для удаленных владельцев)

- **Исправлена типизация в Django management командах**:
  - Добавлены аннотации типов: `def handle(self, *args: Any, **kwargs: Any) -> None:`
  - Использованы минимальные `# type: ignore[attr-defined]` для Django managers и style helpers
  - Переименованы переменные в `add_products.py` для избежания конфликтов типов
  - Все команды проходят проверку mypy без ошибок

### Moderator/Owner Logic Fix
- **Исправлена логика прав доступа для модераторов-владельцев**:
  - Проблема: модератор не мог редактировать контент своего собственного товара/поста
  - Обновлена логика в `get_form()` для `ProductUpdateView` и `BlogPostUpdateView`
  - **Модератор-владелец (свой контент)**: видит ВСЕ поля включая owner и is_published (полный контроль)
  - **Модератор чужого контента**: видит ТОЛЬКО owner и is_published (может переназначить владельца и изменить публикацию)
  - **Обычный владелец**: видит все поля КРОМЕ owner (может редактировать контент и is_published, но не может менять владельца)
  - Логика: модератор-владелец имеет полный контроль над своим контентом, модератор чужого может только управлять владельцем и публикацией

### Auto-Login Fix
- **Исправлен автоматический логин после регистрации**:
  - Изменен порядок операций в `UserRegisterView.form_valid()`
  - Проблема: `form.save()` вызывался дважды - сначала вручную, затем через `super().form_valid()`
  - Решение: сначала вызываем `super().form_valid()` для создания `self.object`, затем `login()`
  - Это предотвращает двойное сохранение и проблемы с сессией

### Management Command для Загрузки Фикстур
- **Команда `python manage.py setup`**: Удобная загрузка всех фикстур одной командой
  - `--users` - загрузка системного пользователя (deleted@system.user)
  - `--groups` - загрузка групп модераторов (Модератор продуктов, Контент-менеджер) с разрешениями
  - `--data` - загрузка данных (категории, товары, блог-посты)
  - Без флагов - загружает всё
  - Идемпотентность: проверяет существование данных перед загрузкой
  - Интерактивное подтверждение при загрузке data если база не пустая
  - Файлы фикстур:
    - `users/fixtures/system_user.json` - системный пользователь
    - `marketplace/fixtures/groups_and_permissions.json` - группы и права
    - `marketplace/fixtures/data.json` - категории, товары, посты

### Moderator Rights Separation
- **Limited Moderator Editing Rights**: Moderators can only change ownership, not content
  - Implemented conditional field pruning in `ProductUpdateView.get_form()` and `BlogPostUpdateView.get_form()`
  - Owner editing their own product/post: sees all fields except owner (cannot change ownership)
  - Moderator editing any product/post: sees ONLY owner field (can reassign ownership but not change content)
  - Added `is_moderator`/`is_manager` context variables in DetailView for template logic
  - Updated templates: "Изменить" button visible to owner OR moderator
  - Business logic: Owners manage content, moderators manage ownership assignment
  
### Owner Management and User Deletion Handling
- **System User for Deleted Owners**: Implemented automatic content preservation when users are deleted
  - Created system user `deleted@system.user` (fixture in `users/fixtures/system_user.json`)
  - Helper function `get_deleted_user()` in both `marketplace/models.py` and `blog/models.py`
  - Uses `on_delete=SET_DEFAULT` with `default=get_deleted_user` for owner ForeignKey fields
  - When a user is deleted, their products/posts automatically transfer to system user
  
- **Owner Reassignment by Moderators**: Moderators can change ownership of products/posts
  - Added `owner` field to `ProductForm` and created `BlogPostForm` with owner field
  - Field visible only to moderators ("Модератор продуктов" and "Контент-менеджер" groups)
  - Ordinary users don't see owner field in forms (auto-assigned to current user on create)
  - Implemented via `get_form()` override in Create/Update views with conditional field removal
  - Extended `get_queryset()` in Update views: moderators can access ALL objects, regular users only their own
  - Moderators can edit any product/post and reassign ownership to different users
  
- **Display Logic for Deleted Owners**:
  - Templates check if `owner.email == "deleted@system.user"`
  - Shows "Владелец удалён" (gray, italic) instead of email for deleted owners
  - Applied to `product_detail.html` and `blogpost_detail.html`
  
- **Business Logic**:
  - Content preservation: Products and blog posts persist even after owner deletion
  - No data loss on user removal
  - Moderators can reassign orphaned content to new owners
  - Owner field remains required ForeignKey (meets project constraints)

## Earlier October 18, 2025

### Owner Visibility and Publishing Permissions
- **Enhanced Queryset Filtering**: Owners now see published items OR their own unpublished items in lists
  - `ProductsListView`: Uses Q objects to filter `Q(is_published=True) | Q(owner=user)` for authenticated non-moderators
  - `BlogPostListView`: Same Q-based filtering for blog posts
  - Moderators/staff still see all items
  - Unauthenticated users see only published items
  
- **Publishing Toggle Access**: Extended to owners in addition to moderators
  - Product cards: Owners can toggle `is_published` status for their own products
  - Blog cards: Owners can toggle `is_published` status for their own posts
  - UI shows "Опубликовать" or "Снять с публикации" based on current status
  - Templates use conditional logic to show toggle only to owner OR moderator
