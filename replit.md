# Overview

A Django-based web application providing an e-commerce marketplace, a blog system, and comprehensive user management with email authentication. It utilizes Bootstrap 5 for responsive design and custom CSS for a unique visual style. The project is structured with modular Django applications, emphasizing separation of concerns to create a robust platform for both selling goods and publishing content. It includes an advanced permission and moderation system to manage content ownership and publication status.

# User Preferences

Стиль общения: простой, повседневный язык.

# System Architecture

## Backend

**Framework**: Django 5.2.7 with Python 3.x.
**Structure**: Modular architecture with `marketplace`, `blog`, `users`, and `config` applications.
**Design Patterns**: Class-Based Views (CBV), Django signals for file cleanup, custom mixins for modal authentication, and custom managers for email-based authentication.
**Authentication**: Email-based using a custom `User` model. Access control via `LoginRequiredMixin` and role-based permissions (owner, moderator, staff).
**File Management**: Automatic cleanup of uploaded files (product photos, blog previews) via Django signals.
**Form Validation**: Custom rules for forbidden words, non-negative prices, file size limits, and unique emails.
**URL Routing**: Namespaces for each application and an administrative interface.
**Permissions & Moderation**:
- `Product` and `BlogPost` models include `owner` and `is_published` fields.
- Custom permission groups: "Product Moderator" and "Content Manager".
- Access logic: Owners can edit their content, moderators can reassign ownership and toggle publication. Unauthenticated users see only published content; staff/moderators see all; owners see their unpublished content.
- Content is preserved upon owner deletion by reassigning to a system user (`deleted@system.user`).

## Data

**Database**: PostgreSQL, configured via environment variables.
**Core Models**: `Product`, `Category`, `BlogPost`, and a custom `User` model.
**Relationships**: `Product` to `Category` with `CASCADE` deletion. File cleanup handled by signal processors for `Product.photo` and `BlogPost.preview`.

## Frontend

**Templating System**: Django templates with inheritance and custom tags.
**Static Assets**: Bootstrap 5.3.8 and custom CSS with variables for consistent gradient design.
**UI/UX**: Modal authentication, responsive design, and gradient color coding. All styling is centralized in `static/css/custom.css`, eliminating inline styles in templates.

# External Dependencies

- **Django 5.2.7**: Web framework.
- **Python 3.x**: Runtime environment.
- **PostgreSQL**: Primary database.
- **dj-database-url**: Database URL parsing.
- **python-dotenv**: Environment variable management.
- **Bootstrap 5.3.8**: Frontend CSS framework and JavaScript components.
- **Django's built-in email backend**: For authentication emails.
- **Django's built-in static files handling**: For static file management.
- **ImageField**: For image uploads.