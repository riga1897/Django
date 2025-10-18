# Overview

This is a Django-based web application providing an e-commerce marketplace, a blog system, and comprehensive user management with email-based authentication. It leverages Bootstrap 5 for responsive design and custom CSS for a distinct visual identity. The project is structured with modular Django apps, emphasizing separation of concerns to create a robust platform for both product sales and content publishing. It includes a sophisticated permission and moderation framework to manage content ownership and publication status effectively.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend

**Framework**: Django 5.2.7 with Python 3.x.
**Structure**: Modular design across `marketplace`, `blog`, `users`, and `config` apps.
**Design Patterns**: Utilizes Class-Based Views (CBVs), Django signals for file cleanup, custom mixins for modal login, and custom managers for email-based user authentication.
**Authentication**: Email-based using a custom `User` model. Access control is managed via `LoginRequiredMixin` and role-based permissions (owner, moderator, staff).
**File Management**: Automatic cleanup of uploaded files (product photos, blog post previews) using Django signals.
**Form Validation**: Custom rules for forbidden words, non-negative prices, file size limits, and email uniqueness.
**URL Routing**: Namespaced URL patterns per app and an admin interface.
**Permissions & Moderation**:
- `Product` and `BlogPost` models include `owner` and `is_published` fields.
- Custom permission groups: "Модератор продуктов" and "Контент-менеджер" with specific rights.
- Access Logic:
    - **Create**: Owner auto-assigned.
    - **Update**: Owner-only for content, moderators can reassign ownership.
    - **Delete**: Owner or moderator.
    - **Toggle Publication**: Owner or moderator.
    - **View Filtering**: Unauthenticated users see published content only; authenticated staff/moderators see all; owners see their own unpublished content.
    - **Owner Deletion**: Content is preserved by reassigning to a system user (`deleted@system.user`).

## Data

**Database**: PostgreSQL, configured for environment-based connections.
**Key Models**: `Product`, `Category`, `BlogPost`, and a custom `User` model.
**Relationships**: `Product` to `Category` with `CASCADE` delete. File cleanup is managed by signal handlers for `Product.photo` and `BlogPost.preview`.

## Frontend

**Template System**: Django templates with inheritance and custom tags.
**Static Assets**: Bootstrap 5.3.8 and custom CSS using variables for a consistent gradient-based design.
**UI Patterns**: Modal authentication, responsive design, and gradient-based color coding.

# External Dependencies

- **Django 5.2.7**: Web framework.
- **Python 3.x**: Runtime environment.
- **PostgreSQL**: Primary database.
- **dj-database-url**: Database URL parsing.
- **python-dotenv**: Environment variable management.
- **Bootstrap 5.3.8**: Frontend CSS framework and JavaScript components.
- **Django's built-in email backend**: For user authentication emails.
- **Django's built-in static files handling**: For managing static assets.
- **ImageField**: For image uploads.