# Overview

This is a Django-based e-commerce platform with three main applications: a marketplace for product listings, a blog for content management, and a user management system. The platform features email-based authentication, a three-tier permission system (owner, moderator, regular user), and AJAX-powered modal windows for login/registration. Content is preserved when owners are deleted through a system user mechanism.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Framework:** Django 5.2.7 with Python 3.x

**Database:** PostgreSQL with support for Replit deployment

**Application Structure:**
- `marketplace` - Product catalog and e-commerce functionality
- `blog` - Blog post management system
- `users` - Custom user authentication and profile management
- `config` - Project-wide settings and URL routing

**Key Design Patterns:**
- **Class-Based Views (CBVs)** - All views use Django's generic CBVs for consistency and reusability
- **Django Signals** - Automatic cleanup of uploaded files (images) when objects are deleted or updated
- **Custom Mixins** - `ModalLoginRequiredMixin` for AJAX-based authentication without page reloads
- **Custom Managers** - Email-based authentication instead of username (in `UserManager`)
- **Role-Based Access Control** - Three-tier permission system using Django's built-in groups and permissions

### Authentication & Authorization

**Custom User Model:**
- Email is the primary authentication field (USERNAME_FIELD)
- Extends Django's AbstractUser
- Additional fields: avatar, phone, country
- Custom UserManager handles user creation with email

**Permission Levels:**
1. **Owner** - Full CRUD access to their own content
2. **Moderator** - Can unpublish and delete content (group-based: "Модератор продуктов", "Контент-менеджер")
3. **Regular User** - Can view published content and manage their own items
4. **Staff/Superuser** - Full administrative access

**Content Visibility Rules:**
- Unauthenticated: See only published content
- Authenticated: See published content OR their own unpublished content
- Moderators/Staff: See all content regardless of publication status

### Data Models

**Product (Marketplace):**
- Fields: name, description, photo, category, price, owner, is_published
- ForeignKey to Category (CASCADE delete)
- ForeignKey to User with SET_DEFAULT to system user on owner deletion
- Custom validation: forbidden words filter, price validation, file size limits

**BlogPost:**
- Fields: title, content, preview, owner, is_published, views_count, created_at, updated_at
- Similar ownership pattern to Product
- View counter for analytics
- Custom permission: `can_unpublish_post`

**Category:**
- Simple name/description model for product organization
- One-to-many relationship with Products

**User:**
- Email-based authentication (unique)
- Optional username field
- Profile fields: avatar, phone, country
- Related names: `products`, `blog_posts`

### Content Preservation Strategy

**System User Pattern:**
- A special "deleted@system.user" account is created on platform initialization
- When a user is deleted, their content is reassigned to this system user instead of being deleted
- Implemented via `SET_DEFAULT` with `get_deleted_user()` callable
- Prevents data loss and maintains content history

### Frontend Architecture

**Template System:**
- Base template with sidebar navigation (`marketplace/base.html`)
- Component-based includes: `product_card.html`, `blogpost_card.html`, `form_field.html`
- Template inheritance for consistent layout

**UI Framework:**
- Bootstrap 5.3.8 for responsive design
- Custom CSS with CSS variables for theming
- Gradient color coding system:
  - Green gradients: Lists, forms, marketplace
  - Red gradients: Delete actions
  - Yellow gradients: Draft/unpublished states

**AJAX Functionality:**
- Modal windows for login/registration (no page reload)
- Form submissions redirect back with modal state preserved via URL parameters
- Safe redirect handling with `url_has_allowed_host_and_scheme()`

### File Management

**Django Signals for Cleanup:**
- `post_delete` signal: Deletes associated files when model instance is deleted
- `pre_save` signal: Deletes old files when new ones are uploaded
- Applies to both Product photos and BlogPost previews

**Media Storage:**
- Products: `products/photos/`
- Blog posts: `blogs/previews/`
- User avatars: (configurable upload path)

### Caching Strategy

**Product List Caching:**
- Cache keys differentiate by user permission level and category
- Anonymous users: cached published products only
- Authenticated users: cached personalized view (published + own)
- Staff/moderators: cached view of all products
- Service layer function: `get_products()` in `marketplace/services.py`

### Management Commands

**Platform Initialization:**
- `setup` - Complete platform setup: clears DB, creates system user, creates permission groups, creates superuser
- `del_all` - Wipes all data and resets ID sequences
- `load_data` - Loads test fixtures (users, products, blog posts)
- `createadmin` - Quick superuser creation

**Test Data:**
- Fixtures include 3 test users with different permission levels
- Groups: "Модератор продуктов", "Контент-менеджер"
- Sample products and blog posts

### Form Validation

**ProductForm:**
- Forbidden words filter (казино, криптовалюта, etc.)
- Price must be non-negative
- Image file size limit: 5MB
- Bootstrap form styling applied automatically

**BlogPostForm:**
- Similar validation patterns
- Auto-applies `form-control` CSS class to fields

**UserForms:**
- Email uniqueness validation
- Case-insensitive email handling
- Password confirmation matching

## External Dependencies

### Core Framework
- **Django 5.2.7** - Web framework
- **PostgreSQL** - Primary database (configured via `dj_database_url`)

### Python Packages
- `python-dotenv` - Environment variable management
- `dj-database-url` - Database URL parsing for deployment

### Frontend Libraries
- **Bootstrap 5.3.8** - CSS framework (self-hosted in `/static/`)
- Custom CSS in `static/css/custom.css`

### Development Tools
- **mypy** - Type checking (100% coverage indicated)
- **ruff** - Python linter
- **black** - Code formatter
- **isort** - Import sorting

### Deployment Configuration
- **Replit-specific settings:**
  - CSRF_TRUSTED_ORIGINS configured for Replit domains
  - CSRF_COOKIE_SAMESITE and SESSION_COOKIE_SAMESITE set to "None" for iframe compatibility
  - Secure cookies enabled when HTTPS is detected

### Environment Variables Required
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode toggle ("True" or other)
- `REPLIT_DEV_DOMAIN` - Auto-configured on Replit
- `REPLIT_DOMAINS` - Comma-separated list of allowed domains
- Database URL (parsed by `dj_database_url`)

### Static Files
- Bootstrap CSS/JS served from `/static/`
- Custom CSS variables for theming
- Media files served from `/media/` in development