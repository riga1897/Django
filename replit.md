# Overview

This repository contains a Django-based multi-application web platform featuring:
- **Marketplace**: E-commerce product catalog with category management
- **Blog**: Content management system for publishing posts
- **Users**: Email-based authentication system with user profiles

The platform implements role-based access control where authenticated users can manage products, while product listings remain publicly accessible. Built with Django 5.2+, Bootstrap 5, and PostgreSQL support for both Replit and Windows environments.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Framework & Technology Stack

**Problem**: Need a robust web framework for building database-driven applications with admin interface
**Solution**: Django 5.2+ web framework with PostgreSQL-compatible database
**Rationale**: Django provides built-in admin interface, ORM, authentication, and follows MTV (Model-Template-View) pattern

## Application Structure

The system consists of three main Django applications:

### 1. Marketplace Application
- **Purpose**: E-commerce product catalog management
- **Models**: 
  - `Category`: Product categorization with name and description
  - `Product`: Product entries with name, description, photo, category (foreign key), price, and timestamps
- **Features**: 
  - CRUD operations (Create/Update/Delete require authentication via LoginRequiredMixin)
  - Public product listings and detail pages (no login required)
  - Image upload with automatic cleanup via signals
  - Form validation with forbidden words filter (казино, криптовалюта, крипта, биржа, дешево, бесплатно, обман, полиция, радар)
  - Price validation (prevent negative values)
  - Image format/size restrictions (max 5MB)

### 2. Blog Application  
- **Purpose**: Content management system for blog posts
- **Models**:
  - `BlogPost`: Posts with title, content, preview image, publication status, view counter, and timestamps
- **Features**: Draft/published status toggle, view counting with atomic F() expressions, image preview with automatic cleanup, list filtering (show/hide drafts)

### 3. Users Application
- **Purpose**: Email-based user authentication and profile management
- **Models**:
  - `User` (extends AbstractUser): Custom user model with email as USERNAME_FIELD
    - Fields: email (unique), avatar, phone, country, username (inherited, optional)
    - Custom UserManager for email-based authentication
- **Features**:
  - User registration with CustomUserCreationForm
  - Email-based login with CustomAuthenticationForm
  - User profile viewing and editing
  - Avatar upload support
  - Welcome email on registration (console backend for development)

## Database Design

**Choice**: Django ORM with relational database (PostgreSQL-ready)
**Design Patterns**:
- Foreign key relationships (Product→Category, Book→Author)
- Automatic timestamp tracking with `auto_now_add` and `auto_now`
- Cascade deletion for related records
- Ordering specifications at model level

## File Storage & Media Management

**Problem**: Need to manage uploaded images efficiently and prevent orphaned files
**Solution**: Django's file storage system with signal-based cleanup
**Implementation**:
- Images stored in `media/` directory with organized subdirectories
- `post_delete` signals: Remove files when model instances are deleted
- `pre_save` signals: Remove old files when images are updated
- Graceful handling of missing images in templates

## Authentication System

**Custom User Model** (`users.User`):
- Email-based authentication (USERNAME_FIELD = "email")
- Extended fields: email (unique), avatar, phone, country
- Username field automatically mirrors email (auto-filled by UserManager)
- Custom UserManager with overridden create_user() and create_superuser() methods
- Integration with Django's built-in auth system
- REQUIRED_FIELDS = [] (only email and password required)

**Authentication Flow**:
- **Modal-Based UI**: Login and registration via Bootstrap modals in base template (no separate auth pages)
- Registration: CustomUserCreationForm with automatic login after successful registration
- Login: CustomAuthenticationForm with email/password fields
- Protected routes: Custom `ModalLoginRequiredMixin` redirects to modal instead of separate page
- Profile management: UserProfileForm for editing user details
- Public access: Product listings and detail pages accessible without login

**Security Features**:
- Safe redirect validation with `url_has_allowed_host_and_scheme()`
- Query parameter encoding via `urlencode()` to prevent URL corruption
- Next parameter preservation through entire login flow
- Protection against open redirect vulnerabilities
- CSRF protection for all forms

## Form Validation

**Marketplace Forms**:
- Forbidden words filter for product names and descriptions
- Price validation (prevent negative values)
- Custom error messages
- Widget customization with Bootstrap classes

## Template Architecture

**Design Pattern**: Template inheritance with base layouts
- **Base Templates**: 
  - `marketplace/base.html`: Main layout with sidebar navigation and embedded auth modals
- **Authentication Modals**: 
  - Login and register modals built into base template using Bootstrap 5
  - Auto-open via URL parameters (`?show_login_modal=1`, `?show_register_modal=1`)
  - JavaScript-based modal management for error handling
  - Next parameter preservation for post-login redirects
- **Reusable Components**: Card templates for products and blog posts
- **Form Fields**: Generic form field template with icon detection based on widget type
- **Styling**: Bootstrap 5.3.8 with custom gradient CSS
- **Color Scheme**: Green gradients for marketplace, contextual colors for actions (red for delete, yellow for drafts)
- **Responsive Design**: Mobile-first approach with responsive modals and layouts

## View Layer Architecture

**Pattern**: Class-Based Views (CBVs) for consistency
- `ListView`: Display collections with filtering support
- `DetailView`: Show individual items with view counting
- `CreateView`/`UpdateView`: Form handling with validation
- `DeleteView`: Confirmation before deletion
- `FormView`: Contact form processing

**Custom Mixins**:
- `ModalLoginRequiredMixin`: Custom authentication mixin for modal-based login
  - Redirects unauthorized users to main page with modal parameter
  - Preserves original destination URL via `next` parameter
  - Validates redirect URLs to prevent open redirect vulnerabilities
  - Uses `urlencode()` for safe query parameter handling

**Custom Behavior**:
- Query filtering in `get_queryset()` (e.g., published posts only)
- Atomic view counting with `F()` expressions
- Success URL configuration with `reverse_lazy`
- Safe redirect validation in authentication views

## Static Asset Management

**Structure**:
- Bootstrap 5.3.8 (minified CSS and JS bundles)
- Custom CSS with CSS variables for theming
- Template tags for media URL generation
- Widget type detection for dynamic form rendering

## Management Commands

**Purpose**: Data seeding and administrative tasks
**Commands**:
- `add_products`: Populate marketplace with test data
- `add_books`: Populate library with test books
- `createadmin`: Create superuser programmatically
- `del_all`: Clean database tables
- `load_from_fixture`: Load data from JSON fixtures

## Configuration Management

**Environment Variables** (via python-dotenv):
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode toggle
- Database configuration (implicit, uses Django defaults)

**Settings Structure**:
- Separated settings in `config/settings.py`
- Media and static files configuration
- Template directories auto-discovery
- App registration with signal initialization

## URL Routing

**Pattern**: Namespaced URL configurations
- App-level URL configs with `app_name`
- Namespace usage in templates: `{% url 'marketplace:product_detail' pk %}`
- Clean URL patterns with descriptive names

## Code Quality & Linting

**Configuration Files**:
- `.flake8`: Python linter configuration (max line length: 119, complexity: 10)
- `.pydocstyle`: Docstring style checker configuration
- `.editorconfig`: Editor settings for consistent code style
- `.pre-commit-config.yaml`: Pre-commit hooks for automated checks

**Linting Tools**:
- **flake8**: Code style and error checking with docstring validation
- **isort**: Import sorting and organization (black-compatible profile)
- **black**: Code formatter (line length: 119)
- **mypy**: Static type checking with Django stubs support

**Standards**:
- Maximum line length: 119 characters
- Import order: Django imports, third-party, local imports (enforced by isort)
- No trailing whitespace or whitespace in blank lines
- Newline at end of all files
- Google-style docstrings

# External Dependencies

## Core Framework
- **Django 5.2+**: Web framework
- **python-dotenv**: Environment variable management

## Frontend
- **Bootstrap 5.3.8**: UI framework (bundled locally)
- Custom CSS with gradient designs and responsive layouts

## Database
- **Django ORM**: Database abstraction layer (PostgreSQL-compatible schema)
- Note: Currently using Django defaults, can be configured for PostgreSQL

## File Storage
- **Django Storage API**: File and image management
- Media files stored in local filesystem (configurable for cloud storage)

## Email (Library App)
- **Django Email Backend**: SMTP email sending for user registration
- Configured sender: `usr.some@yandex.ru`

## Template System
- **Django Template Language**: Template rendering
- Custom template tags for media filtering and widget detection

## Admin Interface
- **Django Admin**: Built-in administration interface
- Customized with list displays, filters, and search capabilities