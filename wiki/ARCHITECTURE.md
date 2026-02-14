# PyArgus Project Structure & Architecture

## Overview

PyArgus is an SSH Bastion server application built with a focus on clean architecture, maintainability, and SOLID principles. The project uses modern Python design patterns and follows best practices for application structure.

## Architecture Principles

### SOLID Principles Applied

- **Single Responsibility Principle (SRP)**: Each class has one reason to change
  - `Logger` handles only logging
  - `DependencyContainer` manages only dependency injection
  - `BaseService` provides only service lifecycle management

- **Open/Closed Principle (OCP)**: Open for extension, closed for modification
  - Abstract base classes (`BaseService`, `ILogger`) for extensibility
  - Service registry for adding new services without modifying core code

- **Liskov Substitution Principle (LSP)**: Subtypes are substitutable for base types
  - All services inherit from `BaseService`
  - All loggers implement `ILogger`

- **Interface Segregation Principle (ISP)**: Clients depend on specific interfaces
  - `ILogger` interface for logging contracts
  - `IDependencyContainer` interface for DI container

- **Dependency Inversion Principle (DIP)**: Depend on abstractions, not concretions
  - Dependency injection container for loose coupling
  - Abstract interfaces for all major components

### Design Patterns Used

1. **Singleton Pattern**
   - `AppConfig`: Single configuration instance across application
   - `ApplicationFactory`: Manages single Application instance

2. **Factory Pattern**
   - `ApplicationFactory`: Creates and manages Application instances
   - Clean interface for application creation

3. **Registry Pattern**
   - `DependencyContainer`: Registry for services
   - `ServiceRegistry`: Registry for application services

4. **Dependency Injection**
   - `DependencyContainer`: Provides services to application components
   - Services receive dependencies via constructor

5. **Abstract Base Class Pattern**
   - `BaseService`: Template for all services
   - `ILogger`, `IDependencyContainer`: Contracts for implementations

## Project Directory Structure

```
pyargus/
│
├── app/                              # Core application package
│   ├── __init__.py                  # Package initialization (public API exports)
│   ├── config.py                    # Configuration management (Singleton)
│   ├── exceptions.py                # Custom exception hierarchy
│   ├── application.py               # Application bootstrap & DI container
│   ├── base_service.py              # Abstract base class for services
│   │
│   ├── api/                         # REST API implementation
│   │   ├── __init__.py
│   │   ├── routes.py                # API endpoints (to be implemented)
│   │   ├── schemas.py               # Pydantic request/response models
│   │   └── handlers.py              # Business logic handlers
│   │
│   ├── security/                    # Security & encryption
│   │   ├── __init__.py
│   │   ├── encryption.py            # AES encryption/decryption
│   │   └── key_validator.py         # SSH key validation
│   │
│   └── utils/                       # Utility modules
│       ├── __init__.py
│       ├── ip_utils.py              # IP address utilities
│       └── port_utils.py            # Port management utilities
│
├── migrations/                       # Database migrations
│   ├── __init__.py
│   └── 001_initial_schema.py        # Initial schema (to be implemented)
│
├── scripts/                         # Standalone scripts
│   ├── __init__.py
│   └── deploy_client.sh             # Client deployment script
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   ├── test_config.py               # Configuration tests
│   ├── test_application.py          # Application tests
│   ├── test_api.py                  # API endpoint tests
│   └── test_security.py             # Security module tests
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .env                             # Local environment (not in git)
├── pytest.ini                       # Pytest configuration
├── .gitignore                       # Git ignore rules
├── DEVREADME.md                     # Development documentation
├── IMPLEMENTATION_PLAN.md           # Step-by-step implementation plan
└── README.md                        # Project documentation

```

## Key Components

### 1. Configuration Management (`app/config.py`)

**Purpose**: Centralized configuration management using Singleton pattern

**Key Classes**:
- `DatabaseConfig`: Database-specific settings
- `APIConfig`: API server settings
- `SecurityConfig`: Security and encryption settings
- `AppConfig`: Main configuration (Singleton)

**Features**:
- Validates configuration on initialization
- Loads from environment variables
- Type-safe dataclass structure
- Single instance across application

**Usage**:
```python
from app import AppConfig

# Get singleton instance
config = AppConfig.get_instance()

# Or load from environment
config = AppConfig.from_env()

# Access settings
print(config.api.port)
print(config.database.database_url)
```

### 2. Exception Hierarchy (`app/exceptions.py`)

**Purpose**: Domain-specific exceptions for better error handling

**Exception Classes**:
- `PyArgusException`: Base exception
- `ConfigurationError`: Configuration issues
- `DatabaseError`: Database operation failures
- `ValidationError`: Data validation failures
- `AuthenticationError`: Authentication failures
- `SSHError`: SSH operation failures
- `EncryptionError`: Encryption/decryption failures
- `ResourceNotFoundError`: Resource not found
- `ResourceConflictError`: Resource conflicts

**Benefits**:
- Specific exception types for different error scenarios
- Easier error handling in calling code
- Better debugging with error codes

### 3. Application Bootstrap (`app/application.py`)

**Purpose**: Single entry point for application initialization

**Key Classes**:

#### `Logger` (Implementation of `ILogger`)
- Concrete logging implementation
- Wraps Python's logging module
- Used throughout application

#### `DependencyContainer` (Implementation of `IDependencyContainer`)
- Service registry using Registry pattern
- Manages singleton service instances
- Prevents circular dependencies

#### `Application`
- Main application orchestrator
- Initializes all components
- Manages application lifecycle

#### `ApplicationFactory`
- Factory pattern for Application creation
- Manages singleton Application instance

**Usage**:
```python
from app import ApplicationFactory, AppConfig

# Create and initialize application
app = ApplicationFactory.create()

# Or with custom config
config = AppConfig.from_env()
app = ApplicationFactory.create(config)

# Access components
logger = app.logger
container = app.container
config = app.config

# Shutdown
app.shutdown()
```

### 4. Base Service Infrastructure (`app/base_service.py`)

**Purpose**: Template for implementing all application services

**Key Classes**:

#### `BaseService` (Abstract)
- Defines service lifecycle: `initialize()`, `shutdown()`
- Provides health check infrastructure
- Common logging interface
- Validation helpers

#### `ServiceRegistry`
- Manages multiple services
- Initializes all services
- Performs health checks
- Registry pattern implementation

**Benefits**:
- Consistent service interface
- Automatic lifecycle management
- Graceful shutdown in correct order
- Health monitoring

**Example Service Implementation**:
```python
from app.base_service import BaseService

class SSHManager(BaseService):
    def __init__(self, logger):
        super().__init__("SSHManager", logger)
    
    def initialize(self):
        super().initialize()
        # SSH-specific initialization
    
    def shutdown(self):
        # SSH-specific cleanup
        super().shutdown()
    
    def health_check(self):
        health = super().health_check()
        health["ssh_keys_loaded"] = True
        return health
```

## Entry Point Usage

### From Command Line

```bash
# Start with defaults
python main.py

# Debug mode
python main.py --debug

# Custom port
python main.py --port 9000

# Production environment
python main.py --environment production --workers 8

# Custom .env file
python main.py --config /etc/pyargus/.env
```

### From Python Code

```python
from app import ApplicationFactory, AppConfig

# Custom configuration
config = AppConfig.from_env()
config.api.port = 9000
config.debug = True

# Create and use application
app = ApplicationFactory.create(config)

# Application is fully initialized and ready
print(f"App running on {app.config.api.host}:{app.config.api.port}")

# Access any registered service
logger = app.container.get("logger")
logger.info("Application is ready")
```

## Data Flow

```
main.py
  ↓
parse_arguments()
  ↓
load_dotenv(.env)
  ↓
create_app_config()
  ↓
ApplicationFactory.create(config)
  ↓
Application.__init__() → _validate_configuration()
  ↓
Application.initialize()
  ├── _register_core_services()
  │   ├── Register: config
  │   ├── Register: logger
  │   └── Register: container
  └── _initialize_components()
      ├── (Database)
      ├── (API)
      ├── (SSH Manager)
      └── (Other services)
  ↓
Application ready for use
```

## Testing Strategy

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_config.py           # Configuration tests
├── test_application.py      # Application bootstrap tests
├── test_api/
│   ├── test_routes.py
│   └── test_handlers.py
├── test_security/
│   ├── test_encryption.py
│   └── test_key_validator.py
└── test_base_service.py     # Service infrastructure tests
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_config.py

# Specific test
pytest tests/test_config.py::test_config_validation
```

## Extending the Application

### Adding a New Service

1. Create service module (e.g., `app/ssh_manager.py`)
2. Inherit from `BaseService`
3. Implement `initialize()` and `shutdown()`
4. Register in `Application._register_core_services()`

```python
from app.base_service import BaseService

class SSHManager(BaseService):
    def __init__(self, logger):
        super().__init__("SSHManager", logger)
    
    def initialize(self):
        super().initialize()
        # Initialize SSH resources
    
    def shutdown(self):
        # Cleanup SSH resources
        super().shutdown()
```

### Adding a New API Endpoint

1. Define schema in `app/api/schemas.py`
2. Implement handler in `app/api/handlers.py`
3. Add route in `app/api/routes.py`

## Best Practices

1. **Always use dependency injection** for loose coupling
2. **Inherit from BaseService** for all manager/service classes
3. **Use abstract interfaces** for all major components
4. **Log at appropriate levels** (debug, info, warning, error)
5. **Validate configuration** on startup
6. **Handle exceptions gracefully** with proper error types
7. **Write tests** for all business logic
8. **Document complex logic** with docstrings

## Performance Considerations

- Singleton pattern for shared resources (config, logger)
- Lazy initialization for expensive resources
- Service registry for fast lookups
- Dependency container for efficient object creation

## Security Considerations

- Environment variables for sensitive config
- Encryption key management
- SSH key validation
- Exception handling prevents information leakage
- Input validation in schemas

## Future Improvements

- [ ] Caching layer for frequently accessed data
- [ ] Rate limiting middleware
- [ ] Request tracing/correlation IDs
- [ ] Metrics collection
- [ ] Configuration hot-reload
- [ ] Plugin system for extensions
