# Сервис управления email-рассылками

## Overview
This project is a Django-based web application for managing email newsletters. Its purpose is to provide a robust platform for managing mailing list recipients, composing messages, scheduling and sending newsletters, and tracking delivery attempts. Key capabilities include user authentication, role-based access control (User and Manager), and performance optimization through caching. The business vision is to deliver a reliable and efficient email marketing tool, focusing on scalability and clear separation of concerns.

## User Preferences
- **Database Configuration (Development)**: Uses Replit PostgreSQL with PG* variables mapped to DB_*.
- **Database Configuration (Production)**: Uses external PostgreSQL database (`project04` on `localhost:5432`).
- All DB settings must be configured via the `.env` file or Replit Secrets.
- The project will be tested on a Windows platform.
- All project settings **MUST** be loaded from the `.env` file, not from system environment variables.
- The `.env` file should **NOT** be committed to Git (include it in `.gitignore`).
- Create an `.env.example` file as a template with empty values.
- All sensitive data (passwords, keys) must be handled exclusively through `.env`.
- Ensure compatibility for Windows:
    - Use `os.path.join()` or `pathlib.Path` for file paths.
    - Ensure cross-platform management commands.
    - Correct handling of static and media files.
    - Correct PostgreSQL operation on Windows.
    - Correct operation in cmd/PowerShell.
- Commands must work in cmd and PowerShell.
- All `.py` files must be in UTF-8 encoding.
- When reading/writing files, specify encoding (`encoding='utf-8'`).
- The `.gitignore` file must include necessary entries for Python, Django, environment variables, Poetry, IDE files, and OS files.
- The `AUTH_USER_MODEL` in settings should be replaced with a custom user model.
- `USERNAME_FIELD` should be set to 'email'.
- Permissions for managers should be defined in `Meta` classes of models.
- The `form_valid()` method in `CreateView` should be overridden to automatically set the owner.
- QuerySets should be filtered by owners.
- Checks should be implemented in templates to restrict access.
- Server-side caching should be configured for performance.
- Logging of main events and application errors is desired.
- Follow the structure described in the `project_root` section.

## System Architecture

### Core Principles
The project utilizes a **layered architecture** with a clear separation of concerns, focusing on reusability and modularity.

### UI/UX Decisions
- All templates use a base template/sub-templates, with dynamic navigation for authenticated users.
- The Home page displays key statistics: total mailings, active mailings, unique recipients, scheduler last run time.
- Separate pages for recipients, messages, mailings, and mailing attempts, each with full CRUD functionalities.
- Unified ID display format: `(id:N)` in card headers, separate ID column in tables.
- Timezone display: `Europe/Moscow` with live updates in the navbar via JavaScript.
- Navigation highlights active links correctly for all sections (Recipients, Messages, Mailings, Attempts, Reports).
- Tables structure:
    - **Mailings List**: Card-based layout with `(id:N)` in title
    - **Attempt History**: Table with ID column, mailing name without duplication
    - **Reports**: Table with separate ID column, no ID duplication in mailing name

### Technical Implementations & Feature Specifications
- **User Management**: Custom `AbstractUser` model with email for authentication (`USERNAME_FIELD = 'email'`), avatar, phone, country. Username automatically set to full email to prevent IntegrityError conflicts. Includes registration with email verification, login, logout, password recovery, and profile management.
- **Recipient Management**: CRUD operations for "Recipient" (email, full name, comment, owner).
- **Message Management**: CRUD operations for "Message" (subject, body, owner).
- **Mailing Management**: CRUD operations for "Mailing" (start/end datetime, status, message, recipients, owner). Statuses: `Created`, `Running`, `Completed`. Includes retry logic for failed mailings and correct datetime field pre-population.
- **Mailing Dispatch**: Implemented via UI and a custom management command (`send_mailing`), using Django's `send_mail()`. Supports manual and scheduled sends, with detailed inline error display for failed attempts.
- **Mailing Attempts**: Records each attempt with status (`Success`, `Failure`), server response, mailing link, recipient, and `trigger_type` (manual, scheduled, command).
- **Run-Based Tracking System**: Solves the re-send dilemma with controlled batch tracking:
    - Each `Mailing` has a `current_run` field (default=1, auto-increments on status reset)
    - Each `Attempt` has a `run_number` field to tag which batch it belongs to
    - Duplicate suppression checks (mailing, recipient, run_number, status=SUCCESS) instead of global checks
    - Allows controlled re-sends: reset mailing to "Created" → `current_run` increments → new attempts created with new run_number
    - Complete audit trail: all attempts preserved, grouped by run number
    - All sending mechanisms (scheduler, manual view, command, form) propagate `mailing.current_run` to `Attempt.run_number`
    - UI displays run numbers (#1, #2, #3...) in attempt history for clear tracking
    - Atomic increment using Django's F() expression prevents race conditions
- **Access Control**:
    - **User Role**: Own CRUD for recipients, messages, mailings, and viewing own statistics. Sees only own data.
    - **Manager Role**: 
        - View all recipients, messages, mailings across all users
        - View list of all service users with activity statistics
        - Block/unblock user accounts (prevents login and mailing execution)
        - Disable/enable individual mailings (sets `is_active` flag)
        - Access to global attempt logs (all users' sending attempts)
        - Access to global reports (statistics for all mailings)
        - Cannot edit/delete others' data (read-only access)
        - Implemented via Django's "Managers" group with custom permissions
- **Caching**: Server-side caching (locmem backend) for performance (e.g., home page statistics, QuerySets) with configurable timeouts and invalidation via Django signals. Per-user caching for home page statistics to prevent data leaks.
- **Automatic Scheduling**: `django-apscheduler` integration for scheduled mailings with optimized configuration:
    - **MemoryJobStore**: Uses in-memory storage instead of DjangoJobStore for task persistence
        - Avoids early DB access during server startup (no circular dependency issues)
        - Eliminates unnecessary DB connection logs during scheduler runs
        - Faster execution (no network overhead to database)
        - Task is static and recreated on each server restart (acceptable trade-off)
    - **Timing Configuration** (via `.env`):
        - `SCHEDULER_FIRST_RUN_DELAY=15`: First check 15 seconds after server launch (ensures complete Django/DB initialization)
        - `SCHEDULER_CHECK_INTERVAL_MINUTES=3`: Subsequent checks every 3 minutes
        - Both values are configurable and can be adjusted for different environments (development vs production)
    - **Persistent Connections**: `CONN_MAX_AGE=600` (10 minutes) prevents constant DB reconnections during scheduler operations
    - **Reliability**: Delayed first run guarantees stable startup without race conditions
- **Audit Trail**: Automatic creation of Attempt records when manually changing mailing status via form, with `trigger_type="manual"` and descriptive server response.
- **Logging**: Logging of major events and errors. Scheduler activity logged with timestamps displayed on homepage.
- **User Management (Manager Feature)**: 
    - List all service users with email, registration date, status (active/blocked)
    - Display user statistics: number of mailings, recipients, total attempts
    - Block/unblock user accounts via toggle button
    - Blocked users cannot login or execute mailings
    - Protection: cannot block self, superusers, or managers (except by superuser)
    - Implemented via `UserManagementListView` and `UserToggleActiveView`
- **Manager Administration Panel** (partially planned):
    - **User Management**: ✅ **IMPLEMENTED** (see above)
    - **Enhanced Data Access**:
        - Recipients, Messages, Mailings lists show data from all users (no `owner=request.user` filter)
        - Each item displays owner information for accountability
        - Managers have read-only access (view only, no edit/delete)
    - **Global Attempt Logs**:
        - View all sending attempts across all users
        - Filter by user, status (success/failure), date range
        - Display: attempt ID, mailing ID, sender, recipient, status, timestamp
    - **Global Reports**:
        - Statistics for all mailings in the system
        - Aggregated success/failure rates across all users
        - Filter by date range, user, status
        - Export functionality for reporting
    - **Mailing Control**:
        - Toggle switch on mailing cards (visible only to managers)
        - Sets `is_active=False` flag on Mailing model
        - AJAX-based toggle without page reload
        - Scheduler skips disabled mailings automatically
        - Disabled mailings remain visible in all lists with visual indicators (dimmed cards, "Отключена" badge)
        - Users cannot manually send disabled mailings (button disabled with tooltip)
        - Manager can re-enable mailings instantly via toggle
    - **Navigation**:
        - New "Management" section in navbar (visible only to managers)
        - Subsections: Users, All Attempts, Global Reports
        - Active link highlighting for management pages

### System Design Choices
- **Core (`apps/core/`)**: Provides an unchanging foundation with `BaseModel`, `OwnedModel`, abstract services (ABC classes), reusable mixins (`OwnerFilterMixin`, `LoggingMixin`, `CacheMixin`), and base permission checks.
- **Applications (`apps/users/`, `apps/mailings/`)**: Contains business logic, models inheriting from core, services using ABCs and mixins, views, forms, and templates.
- **Configuration (`config/`)**: Project settings, utilizing `load_dotenv()` from `settings.py`.
- **ABC (Abstract Base Classes)**: Define contracts for services; implementations reside in separate classes.
- **Mixins**: Used for DRY principle, composition over inheritance, and modularity for features like owner filtering, logging, and caching.
- **Type Safety & 100% Type Coverage**: 
    - **Requirement**: Project must maintain 100% type coverage with zero mypy errors in both global and Poetry environments
    - **Implementation Strategy**:
        - All Django model fields explicitly typed with field type annotations
        - Generic service pattern: `BaseCRUDService(Generic[T])` enables concrete return types for all CRUD operations
        - Targeted `type: ignore` directives for Django framework limitations:
            - `type: ignore[override]` for UserManager signature mismatches with AbstractBaseUser
            - `type: ignore[attr-defined]` for Django ORM attributes (owner_id, queryset, input_formats, etc.)
            - `type: ignore[union-attr]` for custom User methods (is_manager()) on request.user
        - Generic type variable `T` propagates through service layer enabling type inference at call sites
        - All service methods return concrete types: `Optional[T]`, `QuerySet[T]`, `List[T]`
    - **Verification**: `poetry run mypy .` must produce "Success: no issues found in X source files"
    - **Maintenance**: Type coverage must be preserved during all future changes
- **Data Validation**: Primarily uses Django Forms and ModelForms. Pydantic validators are used for complex cases.
- **Code Quality**: Enforced by flake8, black, isort, and pre-commit hooks.
- **Testing**: `pytest-django` with a 100% code coverage target, parallel execution, and database reuse. TDD approach is mandatory.

### Database Schema & Relations
The project uses a relational data model with clearly defined relationships:
- **User**: 1:M relationships with Recipient, Message, and Mailing (ownership).
- **Mailing**: M:1 with Message; M:M with Recipient; 1:M with Attempt.
- All models (Recipient, Message, Mailing) have a ForeignKey to User via `OwnedModel`.
- Integrity constraints include `unique_together = [["email", "owner"]]` in `Recipient` model and `CASCADE` deletion for all relationships.

## External Dependencies

### Core
- **Backend Framework**: Django 5.2.7
- **Python Version**: 3.13
- **Database**: PostgreSQL (`psycopg2-binary==2.9.10`)
- **Package Manager**: Poetry
- **Configuration**: `python-dotenv==1.1.1`
- **Image Processing**: `Pillow==11.3.0`
- **HTTP Requests**: `requests==2.32.5`
- **Email Backend**: `django.core.mail.backends.smtp.EmailBackend`

### Validation
- **Pydantic**: `pydantic==2.11.10`
- **Pydantic Settings**: `pydantic-settings==2.11.0`

### Testing
- **pytest**: `pytest==8.4.2`
- **pytest-django**: `pytest-django==4.11.1`
- **pytest-cov**: `pytest-cov==7.0.0`
- **pytest-xdist**: `pytest-xdist==3.8.0`
- **pytest-mock**: `pytest-mock==3.15.0`
- **pytest-env**: `pytest-env==1.1.5`
- **factory-boy**: `factory-boy==3.3.3`

### Code Quality
- **flake8**: `flake8==7.3.0`
- **black**: `black==25.1.0`
- **isort**: `isort==6.0.1`
- **pre-commit**: `pre-commit==4.3.0`
- **mypy**: `mypy==1.17.1`

### Optional
- **django-apscheduler**: for scheduled mailings