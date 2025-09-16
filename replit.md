# Django Student Management System

## Overview

This is a Django web application built for managing students and courses. The project follows Django's standard architecture with separate apps for students and courses functionality. It's currently in early development with basic views, URL routing, and template structure established. The application includes comprehensive test coverage and is configured for development deployment on Replit.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Framework and Structure
- **Django 5.2.6**: Main web framework providing MVC architecture
- **Project Structure**: Standard Django layout with `config` as the main project directory and separate apps for `students` and `courses`
- **App Organization**: Modular design with dedicated apps handling specific functionality domains

### URL Routing Architecture
- **Namespace-based routing**: Uses Django's namespace feature to organize URLs by app (`students:` and `courses:`)
- **RESTful patterns**: URLs follow logical patterns like `/students/show_data/`, `/students/list/`, `/courses/list/`
- **Admin integration**: Standard Django admin panel at `/admin/`

### View Layer Design
- **Function-based views**: All views currently implemented as simple functions rather than class-based views
- **Template rendering**: Uses Django's template system for HTML generation
- **Form handling**: Basic POST/GET request handling with CSRF protection
- **Response patterns**: Mix of HttpResponse and template rendering depending on use case

### Template System
- **App-specific templates**: Templates organized under `students/templates/students/` following Django conventions
- **Base HTML structure**: Simple HTML templates with form handling and CSRF token integration
- **Responsive design ready**: Meta viewport tags included for mobile compatibility

### Data Layer
- **Django ORM**: Uses Django's built-in ORM (currently no models defined)
- **SQLite**: Default Django database (no custom database configuration visible)
- **Migrations**: Standard Django migration system in place

### Security Architecture
- **CSRF Protection**: Enabled in middleware and templates
- **Debug mode**: Currently enabled for development
- **Secret key**: Development secret key in use (needs production replacement)
- **Trusted origins**: Configured for Replit deployment

### Testing Strategy
- **Comprehensive test coverage**: Extensive test suites for views, URLs, templates, and app configuration
- **Test organization**: Separate test files for different components
- **Coverage reporting**: HTML coverage reports generated in `htmlcov/` directory
- **Multiple test types**: Unit tests, integration tests, and template rendering tests

## External Dependencies

### Core Framework
- **Django 5.2.6**: Main web framework for backend functionality

### Development Tools
- **Coverage.py**: Code coverage analysis and reporting
- **Django Test Framework**: Built-in testing capabilities

### Deployment Configuration
- **Replit hosting**: Configured with specific host allowances and CSRF trusted origins
- **WSGI/ASGI**: Standard Django deployment interfaces configured

### Template Dependencies
- **Django Template Engine**: Built-in template system for HTML rendering
- **CSRF middleware**: For form security

Note: The application appears to be in early development stage with placeholder views and minimal model implementation. Database models and more complex business logic would typically be added as development progresses.