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