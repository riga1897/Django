# Overview

This is a Django-based web application featuring multiple independent projects within a monorepo structure. The main application is a marketplace and blog platform with product catalog management, blog post publishing, and contact functionality. Additional standalone Django projects (library and students) are included for educational/demonstration purposes.

The application uses Django's class-based views extensively, implements image upload functionality with automatic cleanup, and features a modern Bootstrap-based UI with custom gradient styling.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Framework & Technology Stack

**Backend Framework**: Django 5.2.6
- Python-based web framework
- Uses Django ORM for database operations
- Implements Model-View-Template (MVT) pattern

**Frontend**: Bootstrap 5.3.8
- Responsive UI framework
- Custom CSS with gradient color schemes
- JavaScript for interactive components

**Template Engine**: Django Templates
- Custom template tags for media file handling
- Template inheritance for DRY principles
- Reusable component templates (cards, forms)

## Application Structure

The repository contains multiple Django projects:

1. **Main Application** (root level) - Marketplace & Blog
2. **Library Application** - Book and author management
3. **Students Application** - Student information system

### Main Application Components

**Marketplace App** (`marketplace/`)
- Product catalog with categories
- Image upload with automatic file cleanup via signals
- Contact form functionality
- CRUD operations for products

**Blog App** (`blog/`)
- Blog post management with draft/published status
- View counter with atomic updates
- Image preview support
- Automatic image cleanup on delete/update

## Data Models

### Marketplace Models

**Category Model**
- Simple categorization system
- One-to-many relationship with products

**Product Model**
- Name, description, price fields
- Image upload to `products/photos/`
- Foreign key to Category
- Timestamps (created_at, updated_at)

### Blog Models

**BlogPost Model**
- Title, content, preview image
- Publication status flag (draft/published)
- View counter
- Automatic timestamp ordering

### Supporting Models (Library/Students)

- Author/Book relationship (library app)
- Student/Group relationship (students app)
- Demonstrates various Django relationship patterns

## File Management Strategy

**Image Handling**
- Uses Django's ImageField with custom upload paths
- Implements signal-based cleanup to prevent orphaned files
- Pre-save signal removes old images on update
- Post-delete signal removes images when model is deleted

**Storage Approach**
- Media files served via Django's static file system
- Custom template filter for media URL generation
- File paths organized by model type

## Form Architecture

**Form Processing**
- Django ModelForms for database-backed forms
- Custom form validation in forms.py
- Bootstrap styling via widget attributes
- Reusable form field template (`form_field.html`)

**Form Types**
- Contact forms (FormView)
- Model-based CRUD forms (CreateView, UpdateView)
- Custom validation logic for email domains

## View Architecture

**Class-Based Views (CBV) Pattern**
- ListView for object collections
- DetailView for single objects with view counting
- CreateView/UpdateView for CRUD operations
- DeleteView with confirmation templates
- FormView for non-model forms

**View Logic**
- Atomic view counter updates using F() expressions
- Query filtering (published vs. draft posts)
- Success URL configuration with reverse_lazy
- Context data customization in get_context_data()

## URL Routing

**URL Structure**
- App-level namespace configuration
- RESTful URL patterns for CRUD operations
- Separate URL configs per app
- Media file serving in DEBUG mode

**URL Patterns**
- `/` - Marketplace product list
- `/blog/` - Blog posts
- `/contacts/` - Contact form
- Admin interface at `/admin/`

## Template Organization

**Template Hierarchy**
- Base template with sidebar navigation
- App-specific template directories
- Reusable components (cards, forms, headers)
- Gradient-based visual design system

**Component Templates**
- `product_card.html` - Reusable product display
- `blogpost_card.html` - Reusable blog post display
- `form_field.html` - Universal form field rendering
- Modal dialogs for image viewing

## Custom Template Tags

**Media Filter**
- Generates proper media URLs
- Handles missing images gracefully
- Widget type detection for conditional rendering

## Management Commands

**Custom Commands**
- `add_products` - Populate test product data
- `del_all` - Clean database tables
- `load_from_fixture` - Load fixture data
- Database sequence reset functionality

## Signal Implementation

**File Cleanup Signals**
- `pre_save` - Removes old files before update
- `post_delete` - Removes files after deletion
- Prevents storage bloat from orphaned files
- Uses Django's storage API for file operations

## Static Assets

**CSS Organization**
- Bootstrap base framework
- Custom CSS with CSS variables for theming
- Gradient color system (green, red, yellow)
- Responsive design utilities

**JavaScript**
- Bootstrap bundle for interactive components
- Minimal custom JavaScript
- Modal functionality for image viewing

## Configuration

**Settings Management**
- Environment variables via python-dotenv
- DEBUG mode configuration
- SECRET_KEY from environment
- Allowed hosts set to wildcard (development)

**Apps Configuration**
- Signal registration in AppConfig.ready()
- Custom app naming via AppConfig
- Modular app structure

## Database Design Decisions

**ORM Usage**
- Django ORM for all database operations
- No raw SQL queries
- Relationship management via ForeignKey
- Automatic migrations system

**Data Integrity**
- CASCADE delete for related objects
- Signal-based cleanup for files
- Atomic operations for counters

# External Dependencies

**Core Framework**
- Django 5.2.6 - Web framework
- Python 3.x (implied by Django version)

**Frontend Libraries**
- Bootstrap 5.3.8 - UI framework (vendored in static/)
- No external CDN dependencies

**Python Packages**
- python-dotenv - Environment variable management
- Pillow (implied by ImageField usage) - Image processing

**Database**
- PostgreSQL (based on sequence reset commands in management commands)
- Database connection configured via Django settings

**File Storage**
- Django's default file storage system
- Local filesystem for media files
- Media served via Django in development mode

**Environment Variables**
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode flag
- Additional settings loaded from .env file