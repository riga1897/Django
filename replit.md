# Django Multi-App Learning Environment

## Overview

This repository contains multiple Django projects that appear to be learning examples demonstrating various aspects of web development with Django. The main projects include a marketplace/e-commerce application, a library management system, a student management system, and a basic catalog application. Each project showcases different Django concepts including models, views, templates, admin interfaces, and management commands.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Framework
The repository uses Django 5.2.6 as the primary web framework with Python as the backend language. Each application follows Django's Model-View-Template (MVT) architecture pattern, with clear separation of concerns between data models, business logic, and presentation layers.

### Project Structure
The repository contains four distinct Django projects:
- **Marketplace**: An e-commerce application for product catalog management
- **Library**: A library management system for books and authors
- **Students**: A student information management system
- **Catalog**: A basic catalog application with contact functionality

### Database Design
Each project uses Django's ORM with models defining relationships:
- **Marketplace**: Category-Product relationship (one-to-many)
- **Library**: Author-Book relationship (one-to-many)
- **Students**: Group-Student relationship (one-to-many)

The main marketplace application uses environment-based database configuration with support for PostgreSQL through dj_database_url, while other projects use default SQLite configurations.

### Frontend Architecture
All applications use Bootstrap 5.3.8 for responsive UI components and styling. The marketplace application implements a sophisticated sidebar navigation system with custom CSS styling. Templates follow Django's template inheritance pattern with base templates providing common layout and navigation elements.

### File Management
The marketplace application includes comprehensive media file handling with custom template tags for image URL processing, supporting product photo uploads through Django's ImageField.

### Management Commands
Each application includes custom Django management commands for:
- Database seeding with test data
- Data cleanup and reset operations
- Fixture loading for consistent test environments

### Configuration Management
Applications use environment variables for sensitive configuration through python-dotenv, with separate development and production settings for debug mode, secret keys, and database connections.

## External Dependencies

### Python Packages
- **Django 5.2.6**: Web framework
- **python-dotenv**: Environment variable management
- **dj-database-url**: Database URL parsing for PostgreSQL support
- **Pillow**: Image processing for product photos (implied by ImageField usage)

### Frontend Dependencies
- **Bootstrap 5.3.8**: CSS framework for responsive design
- **Bootstrap Bundle JS**: JavaScript components for interactive elements

### Database Support
- **SQLite**: Default database for development
- **PostgreSQL**: Production database support through dj-database-url configuration

### Static Assets
Each application maintains its own static file structure with Bootstrap CSS and JavaScript bundles, ensuring consistent styling across all projects while maintaining separation of concerns between different learning modules.