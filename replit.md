# Overview

This is a Django-based multi-application web platform that includes three main modules: a marketplace/e-commerce system, a blog, and supporting applications (library and students). The project demonstrates a comprehensive Django implementation with product catalog management, blog posting capabilities, and educational content management.

The platform features:
- **Marketplace**: Full CRUD functionality for products and categories with image uploads, pricing, detailed views, create/update/delete operations
- **Blog**: Content management system with draft/publish workflow, view counting, image previews, and complete CRUD operations
- **Library**: Book and author management system
- **Students**: Student and group management with course tracking

The application uses Django's class-based views extensively, implements custom template tags, includes Bootstrap 5 for responsive UI with unified form styling system, and manages media files for product/blog images.

# Recent Changes

## October 3, 2025
- ✅ Implemented full CRUD functionality for Marketplace products (matching Blog capabilities)
- ✅ Created unified form styling system with `_form_field.html` partial template
- ✅ Added custom `widget_type` template filter for safe widget type detection
- ✅ Unified form design across Blog and Marketplace with consistent Bootstrap styling, gradients, icons, and animations
- ✅ Fixed PostgreSQL database connection using `dj_database_url` for Replit environment
- ✅ Standardized URL patterns: all product URLs use `product/<int:pk>/...` convention
- ✅ Removed authentication requirements (user login/registration not needed)
- ✅ Removed user menu ("Пользователь") from sidebar navigation
- ✅ Fixed blog post visibility: detail pages now accessible for all posts (published/unpublished) via direct URL
- ✅ List views continue to filter by publication status (show only published, or all with ?show_drafts=1)
- ✅ Unified detail page styling: Both marketplace products and blog posts use same design approach
  - Product detail pages: Green gradient headers with shopping cart icon
  - Blog detail pages: Purple gradient headers with book icon
  - Both use same layout structure: hero section, image card, info card with gradients, icons, and animations
  - Single template for all blog posts (published and drafts) with conditional status badges
  - Responsive Bootstrap grid, shadow effects, hover animations on buttons

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Django 5.2.6** as the primary web framework
- **Python** for all backend logic
- Environment-based configuration using `python-dotenv` for managing secrets and settings
- Multiple Django apps organized within a single project (`config` as the main settings module)

## Application Structure

### Core Applications
1. **Marketplace App**
   - Product and Category models with foreign key relationships
   - Image upload handling for product photos
   - Custom management commands for data fixtures and database seeding
   - Template tag filters for media URL handling and widget type detection
   - Full CRUD operations using CreateView, UpdateView, DeleteView
   - Class-based views (ListView, DetailView) for product display
   - Contact form with FormView implementation
   - Unified form styling with shared `_form_field.html` partial template

2. **Blog App**
   - BlogPost model with publishing workflow (draft/published states)
   - View count tracking using F() expressions to prevent race conditions
   - List views filter posts by publication status (published only by default, all with ?show_drafts=1)
   - Detail views accessible for any post via direct URL (no authentication required)
   - Image preview support with modal display
   - CRUD operations using CreateView, UpdateView, DeleteView
   - Post editing returns to detail page after save (allows toggling publish status without errors)

3. **Library App** (Separate Django project structure)
   - Author and Book models with one-to-many relationships
   - Complete CRUD interface for book management
   - Custom management commands for test data population

4. **Students App** (Separate Django project structure)
   - Student and Group models with course year choices
   - Generic model (MyModel) demonstrating timestamp tracking
   - Management commands for database operations

## Database Architecture
- **PostgreSQL** (implied by database reset commands using `ALTER SEQUENCE`)
- Models use Django ORM with:
  - Auto-incrementing primary keys
  - Foreign key relationships with CASCADE deletion
  - Timestamp fields (auto_now_add, auto_now)
  - Choice fields for constrained values (student years, publication status)
  - Image fields for media uploads

## Frontend Architecture
- **Bootstrap 5.3.8** for responsive UI components
- Custom CSS for sidebar navigation and card-based layouts
- Template inheritance with base templates
- Reusable template components (product cards, blog cards)
- Modal dialogs for image viewing
- Static file serving in development mode

## Media & Static Files
- Separate media upload paths for different content types:
  - `products/photos/` for marketplace items
  - `blogs/previews/` for blog post images
- Static files served from `/static/` directory
- Media files configured with MEDIA_URL and MEDIA_ROOT

## URL Routing
- Namespace-based URL patterns for app isolation
- RESTful URL structure for CRUD operations
- App-specific URL configuration using AppConfig

## Admin Interface
- Customized ModelAdmin classes for each model
- List display customization with filtering and search
- Inline editing for boolean fields (is_published)
- Custom admin actions and field groupings

## Forms & Validation
- Django Forms for contact functionality
- ModelForm usage in generic editing views
- CSRF protection on all POST requests
- Unified form styling system using `_form_field.html` partial template
- Custom `widget_type` template filter for widget detection (Textarea, Select, CheckboxInput, FileInput)
- Bootstrap form styling with gradients, icons, shadows, and animations
- Color-coded form headers (blue for Marketplace, purple for Blog)
- Automatic widget rendering based on field type
- File upload previews with image preview functionality

## Design Patterns

### View Layer
- Extensive use of class-based views for consistency
- Mixin usage for access control (UserPassesTestMixin)
- Override of get_queryset() for conditional filtering
- Custom context data injection via get_context_data()

### Data Management
- Custom management commands for:
  - Database seeding
  - Fixture loading
  - Data cleanup with sequence resets
- Atomic operations for view count updates using F() expressions

### Template Architecture
- DRY principle with template inheritance
- Reusable components via include tags (shared form fields, cards)
- Custom template tags for media URL processing and widget type detection
- Context-aware rendering (draft visibility based on user roles)
- Unified form field rendering using `_form_field.html` partial
- Widget-specific rendering logic (textarea, select, checkbox, file input, text input)

### Access Control
- Staff/superuser checks for administrative features
- Conditional content visibility (published vs draft posts)
- URL-based filtering for showing/hiding draft content

# External Dependencies

## Python Packages
- **Django 5.2.6**: Web framework
- **python-dotenv**: Environment variable management for configuration

## Frontend Libraries
- **Bootstrap 5.3.8**: CSS framework for responsive design (locally hosted)
- Bootstrap Bundle JS for interactive components

## Database
- **PostgreSQL**: Primary database (inferred from SQL commands using PostgreSQL-specific syntax)
- Database connection configured via environment variables

## File Storage
- Local filesystem for media uploads
- Organized upload directories by content type
- Development-mode static/media file serving

## Environment Configuration
- SECRET_KEY via environment variable
- DEBUG mode controlled by environment variable
- Database credentials managed through environment variables
- UTF-8 encoding specification for proper character handling