# Overview

This is a Django-based web application with three main components: a marketplace (e-commerce product catalog), a blog system, and user management with email-based authentication. The application uses Bootstrap 5 for styling and includes custom CSS for visual enhancements. The project follows Django best practices with proper separation of concerns across apps.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture

**Framework**: Django 5.2.7 with Python 3.x

**Project Structure**: Multi-app Django project with modular design:
- `marketplace/` - Product catalog and e-commerce functionality
- `blog/` - Blog post management system
- `users/` - Custom user authentication and profile management
- `config/` - Project-level settings and URL routing

**Design Patterns**:
- Class-Based Views (CBVs) for CRUD operations (ListView, DetailView, CreateView, UpdateView, DeleteView)
- Django signals for automatic cleanup of uploaded files when models are deleted or updated
- Custom mixins (`ModalLoginRequiredMixin`) for authentication flow with modal-based login
- Custom managers (`UserManager`) for email-based user creation

## Data Architecture

**Database**: PostgreSQL (configured via `dj_database_url` for environment-based connection strings)

**Key Models**:
- `Product` - Product catalog with photos, categories, pricing, and timestamps
- `Category` - Product categorization with name and description
- `BlogPost` - Blog entries with preview images, publish status, and view counts
- `User` - Custom user model extending `AbstractUser` with email as username field, plus avatar, phone, and country fields

**Model Relationships**:
- Product → Category (ForeignKey with CASCADE delete)
- Signal handlers manage file cleanup for Product.photo and BlogPost.preview

## Authentication & Authorization

**Authentication Strategy**: Email-based authentication instead of username
- Custom `User` model with `email` as `USERNAME_FIELD`
- Custom `UserManager` for user creation
- `AUTH_USER_MODEL = "users.User"` configured in settings

**Access Control**:
- Django's built-in `LoginRequiredMixin` extended with custom `ModalLoginRequiredMixin`
- Modal-based login flow that redirects to homepage with login modal open
- Safe URL validation to prevent open redirects

## Frontend Architecture

**Template System**: Django templates with Bootstrap 5
- Template inheritance for consistent layout
- Custom template tags in `marketplace/templatetags/my_tags.py` for media URL handling and widget type detection

**Static Assets**:
- Bootstrap 5.3.8 (CSS and JavaScript bundle)
- Custom CSS with CSS variables for consistent color scheme and gradient system
- Media files handled through Django's storage system with environment-specific paths

**UI Patterns**:
- Modal-based authentication flows
- Gradient-based visual design system (green for lists/contacts, red for delete actions, yellow for drafts)
- Responsive design using Bootstrap grid system

## File Management

**Strategy**: Automatic cleanup via Django signals
- `pre_save` signal deletes old images when replaced
- `post_delete` signal removes associated files when model instances are deleted
- Applies to both Product photos and BlogPost previews
- Uses Django's storage API (`delete(save=False)`)

## Form Validation

**Custom Validation Rules**:
- Forbidden words filter for Product names and descriptions
- Price validation (non-negative)
- File size limits (5MB for product photos)
- Email uniqueness and normalization for user registration

## URL Routing

**Structure**: Namespaced URL patterns per app
- `marketplace:` prefix for product-related URLs
- `blog:` prefix for blog-related URLs  
- `users:` prefix for authentication and profile URLs
- Admin interface at `/admin/`

# External Dependencies

## Core Framework
- **Django 5.2.7** - Web framework
- **Python 3.x** - Runtime environment

## Database
- **PostgreSQL** - Primary database (configured via environment variables)
- **dj-database-url** - Database URL parsing for environment-based configuration

## Environment Management
- **python-dotenv** - Environment variable management from `.env` files

## Email
- Django's built-in email backend (configured via `EMAIL_BACKEND` setting)
- Used for user registration and password reset flows

## Media & Static Files
- Django's built-in static files handling
- File uploads stored in `MEDIA_ROOT` with `MEDIA_URL` serving
- ImageField handling for product photos and blog previews

## Frontend Libraries
- **Bootstrap 5.3.8** - CSS framework and JavaScript components
- Custom CSS extending Bootstrap with gradient system and color variables

## Development Tools
- **mypy** - Static type checking (configured with django-stubs plugin)
- **ruff** - Fast Python linter (replaces flake8)
- **black** - Code formatter
- **isort** - Import sorter
- **pytest-django** - Testing framework
- Type hints used throughout codebase for better IDE support and error detection

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

### Permissions and Moderation Framework
- **Models**: Added ownership and publication control
  - `Product`: Added `owner` (ForeignKey to User) and `is_published` (BooleanField, default=False)
  - `BlogPost`: Added `owner` (ForeignKey to User)
  - Custom permissions: `can_unpublish_product` and `can_unpublish_post`
  
- **Permission Groups** (via fixtures):
  - **Модератор продуктов** (Product Moderators): can_unpublish_product, delete_product
  - **Контент-менеджер** (Content Managers): can_unpublish_post, delete_blogpost
  
- **Access Control Logic**:
  - **Create**: Automatically assigns current user as owner
  - **Update**: Only owner can edit their content
  - **Delete**: Owner OR moderator (group-based) can delete
  - **Toggle Publication**: Only moderators can toggle is_published via Bootstrap Switch
  - **View Filtering**: Unauthenticated users see only published content; authenticated staff/moderators see all
  
- **UI Implementation**:
  - Bootstrap Switch toggles in product/post card footers for moderators (positioned bottom-right)
  - Publication status badges (green "Опубл." / yellow "Черн.") shown to authenticated non-moderators only
  - Conditional edit/delete buttons (owner-only, positioned top-right in card footer)
  - Detail buttons ("Подробно"/"Читать") positioned left in card footer
  - All buttons have uniform width (min-width: 85px)
  - Form-based toggle with auto-submit on change
  - Fixed sidebar navigation with scrollable content area
  
- **CSRF Configuration**:
  - Added CSRF_TRUSTED_ORIGINS for Replit domains
  - Configured SameSite=None and Secure cookies for iframe compatibility
  - Full support for Replit development environment

- **Migrations**: Used project-approved `default=1` approach for adding owner to existing records
  - Documented in `docs/DEVELOPMENT.md` as acceptable practice for this project

### Earlier Changes

- **Documentation**: Fully rewrote `docs/DEVELOPMENT.md` to match current project structure
  - Replaced generic mailings examples with marketplace/blog/users
  - Updated structure to reflect tests.py in each app (not separate tests/ directory)
  - Fixed all view names (ProductsListView instead of ProductListView)
  - Added complete FORBIDDEN_WORDS list (9 words)
  - Included real examples from User, Product, BlogPost models
  - Added pytest-django testing guidelines
  - Added migration best practices section
  
- **Code Quality**: Configured ruff linter
  - Added exclude list for virtual environments (.venv, .local)
  - Fixed code style issues (B007, SIM105)
  - All linters passing: mypy (0 errors), ruff (all checks passed)
  
- **Type Annotations**: Full type coverage achieved
  - All models, views, forms, signals typed
  - mypy.ini configured with django-stubs plugin
  - Success: no issues found in 47 source files