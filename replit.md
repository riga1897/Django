# Overview

This project is a Django platform featuring three core applications: an e-commerce marketplace, a blog, and a user management system. It supports email-based authentication, a three-tiered access control system, and uses AJAX modals for login/registration. A key feature is the automatic preservation of content upon user deletion. The platform emphasizes code quality with centralized CSS styling, 100% MyPy type coverage, and passes all linting checks (ruff, black, isort). The business vision is to provide a robust, scalable, and maintainable web platform for diverse online functionalities.

# User Preferences

Стиль общения: простой, повседневный язык.

# System Architecture

## Backend

**Framework**: Django 5.2.7 with Python 3.x.
**Structure**: Modular architecture with `marketplace`, `blog`, `users`, and `config` applications.
**Design Patterns**: Utilizes Class-Based Views (CBV), Django signals for file cleanup, custom mixins for modal authentication, and custom managers for email authentication.
**Authentication**: Email-based with a custom `User` model. Access controlled via `LoginRequiredMixin` and role-based permissions (owner, moderator, staff).
**Access Control**:
- Three-tiered system:
    - **Moderator-owner**: Full control, sees all fields including owner and `is_published`.
    - **Moderator (other's content)**: Sees only owner and `is_published` (can reassign owner and change publication status).
    - **Regular owner**: Sees all fields except owner (can edit content and `is_published`, but not owner).
    - Regular users (not owner, not moderator) do not see the owner of others' records.
- Content is preserved upon user deletion by reassigning it to a system user (`deleted@system.user`).
**File Management**: Automatic cleanup of uploaded files (product photos, blog previews) using Django signals.
**Validation**: Custom rules for forbidden words, non-negative prices, file size limits, and unique emails.
**URL Routing**: Namespaced URLs for each application and an administrative interface.

## Data

**Database**: PostgreSQL, configured via environment variables.
**Key Models**: `Product`, `Category`, `BlogPost`, and a custom `User` model.
**Relationships**: `Product` linked to `Category` with cascade deletion. File cleanup for `Product.photo` and `BlogPost.preview` via signal processors.

## Frontend

**Templating**: Django templates with inheritance and custom tags.
**Static Resources**: Bootstrap 5.3.8 and custom CSS with variables for a consistent gradient design.
**UI/UX**: Features AJAX-powered modal authentication, responsive design, and gradient color coding. All styles are centralized in `static/css/custom.css`, eliminating inline styles.

# External Dependencies

- **Django 5.2.7**: Web framework.
- **Python 3.x**: Execution environment.
- **PostgreSQL**: Primary database.
- **dj-database-url**: For parsing database URLs.
- **python-dotenv**: For environment variable management.
- **Bootstrap 5.3.8**: Frontend CSS framework and JavaScript components.
- **Django's built-in email backend**: For authentication emails.
- **Django's built-in static files handling**: For static asset management.
- **ImageField**: For image uploads.