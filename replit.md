# Overview

This Django platform integrates a marketplace (e-commerce), a blog, and user management. Key features include email-based authentication, a three-tiered access control system, AJAX modal windows for login/registration, and automatic content preservation upon user deletion. The project emphasizes clean code practices with centralized CSS, 100% mypy type coverage, and passes all linters (ruff, black, isort). The business vision is to provide a robust, scalable web platform for various online activities.

# User Preferences

Стиль общения: простой, повседневный язык.

# System Architecture

## Backend

**Framework**: Django 5.2.7 with Python 3.x.
**Structure**: Modular architecture comprising `marketplace`, `blog`, `users`, and `config` applications.
**Design Patterns**: Utilizes Class-Based Views (CBV), Django signals for file cleanup, custom mixins for modal authentication, and custom managers for email authentication.
**Authentication**: Email-based with a custom `User` model. Access control is managed via `LoginRequiredMixin` and role-based permissions (owner, moderator, staff).
**File Management**: Automatic cleanup of uploaded files (product photos, blog previews) using Django signals.
**Form Validation**: Custom rules enforce constraints like forbidden words, non-negative prices, file size limits, and unique emails.

### Access Control and Moderation

- `Product` and `BlogPost` models include `owner` and `is_published` fields.
- Custom permission groups: "Product Moderator" and "Content Manager".
- Access Logic: Owners can edit their content; moderators can reassign ownership and change publication status.
- Unauthorized users see only published content. Staff/moderators see all content. Owners see their unpublished content.
- Content is preserved upon owner deletion by reassigning it to a system user (`deleted@system.user`).

### Three-Tiered Access System
- **Owner-Moderator**: Full control, sees all fields including `owner` and `is_published`.
- **Moderator of Others' Content**: Sees only `owner` and `is_published` (can reassign owner and change publication).
- **Regular Owner**: Sees all fields except `owner` (can edit content and `is_published` but not change owner).
- **Regular User (non-owner, non-moderator)**: Does not see owner information for others' records.
- Owner information is hidden from unauthorized users in product/post details.

### Content Preservation
- Automatic content preservation when a user is deleted via the system user `deleted@system.user`.
- Moderators can reassign ownership of products and posts.
- The `setup` command automatically creates the system user during platform initialization.

## Data

**Database**: PostgreSQL, configured via environment variables.
**Core Models**: `Product`, `Category`, `BlogPost`, custom `User` model.
**Relationships**: `Product` to `Category` with cascade deletion. File cleanup for `Product.photo` and `BlogPost.preview` via signal processors.

## Frontend

**Templating System**: Django templates with inheritance and custom tags.
**Static Resources**: Bootstrap 5.3.8 and custom CSS with variables for consistent gradient design.
**UI/UX**: Features modal authentication, responsive design, and gradient color coding. All styles are centralized in `static/css/custom.css`, eliminating inline styles.

# External Dependencies

- **Django 5.2.7**: Web framework.
- **Python 3.x**: Execution environment.
- **PostgreSQL**: Primary database.
- **dj-database-url**: Database URL parsing.
- **python-dotenv**: Environment variable management.
- **Bootstrap 5.3.8**: Frontend CSS framework and JavaScript components.
- **Django's built-in email backend**: For authentication emails.
- **Django's built-in static files handling**: For static asset management.
- **ImageField**: For image uploads.

# Management Commands

## Core Commands

**`setup`** - Platform Initialization
```bash
python manage.py setup
```
Performs complete platform initialization:
1. Applies all database migrations
2. Creates system user `deleted@system.user`
3. Creates permission groups ("Product Moderator" and "Content Manager")
4. Creates superuser (admin@example.com / admin123)

⚠️ **Important**: This command is safe to run multiple times - it won't create duplicates.

**`del_all`** - Complete Data Cleanup
```bash
python manage.py del_all
```
Deletes all data from the database in the correct order:
1. Blog posts
2. Products
3. Users (except system user)
4. Categories

⚠️ **Warning**: This command deletes ALL data without recovery!

## Additional Commands

**`load_data_from_fixture`** - Load Test Data
```bash
python manage.py load_data_from_fixture
```
Loads test data for development and testing from `marketplace/fixtures/data.json`:
- 3 test users (password for all: test123):
  - test1@example.com - Ivan Petrov (regular user)
  - test2@example.com - Maria Sidorova (product moderator)
  - test3@example.com - Alexey Smirnov (content manager)
- 3 categories (Electronics, TVs, Headphones)
- 6 products
- 3 blog posts

⚠️ **Important**: Run this command only after `setup`, as test data depends on the system user and permission groups.

**`createadmin`** - Create Superuser
```bash
python manage.py createadmin
```
Creates a superuser with email `admin@example.com` and password `admin123`.

## Recommended Workflow

### Clean Platform
```bash
python manage.py del_all      # Clear all data
python manage.py setup         # Initialize platform
```

### Platform with Test Data
```bash
python manage.py del_all                 # Clear all data
python manage.py setup                   # Initialize platform
python manage.py load_data_from_fixture  # Load test data
```

## Updating Test Data

If you've made changes to test data manually and want to update the fixture:

```bash
python -Xutf8 manage.py dumpdata users.User marketplace.Category marketplace.Product blog.BlogPost --indent 4 --output marketplace/fixtures/data.json
```

⚠️ **Important**: After export, manually remove the system user and admin from the fixture, keeping only test users.

# Recent Changes

## October 18, 2025

### Owner Information Hidden from Regular Users (Latest Update)
- **Owner information hidden from regular users**: Owner email now displays only to content owner and moderators
- Modified conditions in `product_detail.html` and `blogpost_detail.html` templates
- Regular authenticated users (non-owners, non-moderators) no longer see owner of others' products and posts

### Third Test User Added
- Created third test user (test3@example.com - content manager)
- Updated `data.json` fixture with 3 test users (regular, product moderator, content manager)
- Fixture contains 6 products and 3 blog posts from different owners
- Updated `load_data_from_fixture` command with correct output

### CSS Centralization and Code Quality
- **Complete style centralization in static/css/custom.css**:
  - Added 40+ new CSS classes to replace all inline styles
  - Class categories: images, forms, cards, buttons, alerts, avatars, utilities
  - All gradients, borders, transitions now in CSS (no inline styles)
  - All templates updated to use CSS classes instead of inline styles

- **Code Quality Fixes**:
  - **Fixed LSP/mypy errors in signals.py**: Added `# type: ignore[attr-defined]` for Django-specific attributes (ImageField.delete(), Model.objects, Model.DoesNotExist)
  - **Fixed LSP errors in apps.py**: Added `# type: ignore[assignment]` for `default_auto_field` (false positive from django-stubs)
  - **All linters pass**: mypy ✅ (53 files), ruff ✅, black ✅, isort ✅, LSP ✅

### Data Management Commands
- **Created `setup.py` command**: platform initialization (migrations, system user, groups, admin)
- **Created `del_all.py` command**: complete data cleanup in correct order
- **Renamed command**: `load_from_fixture.py` → `load_data_from_fixture.py`
- **Split logic**: setup prepares platform, load_data_from_fixture loads test data
- **Created clean fixture**: `data.json` contains only test data (no system users)
- **Fixed deletion order**: content → products → users → categories (prevents FK violations)

### Fixtures
- `users/fixtures/system_user.json` - system user deleted@system.user
- `marketplace/fixtures/groups_and_permissions.json` - permission groups
- `marketplace/fixtures/data.json` - test data (3 users, 3 categories, 6 products, 3 posts)

### Three-Tiered Form Access System
- Moderator-owner sees all fields (owner + is_published + content)
- Moderator of others' content sees only owner and is_published
- Regular owner sees everything except owner (content + is_published)
- Automatic field hiding via `get_form()` and custom logic in views

### AJAX Authentication via Modal Windows
- Login and registration via AJAX without page reload
- Automatic login after successful registration
- Validation error handling with display in modal windows
- Redirect only on successful authentication

### Email-Based Authentication
- Custom User model with email as USERNAME_FIELD
- Custom UserManager for creating users via email
- Email uniqueness at database level

### Data Models
- Product: products with photo, price, category, owner
- BlogPost: posts with preview, view counter, owner
- Category: product categories
- User: custom model with email, avatar, phone, country

### Automatic File Cleanup
- Django signals for deleting files when records are deleted/updated
- Handling for Product.photo and BlogPost.preview
- Safe deletion with existence checks
