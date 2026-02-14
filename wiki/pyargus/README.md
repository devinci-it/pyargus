# wiki/pyargus/ - Module Documentation Index

## Overview

This directory contains detailed documentation for each PyArgus module and package. Each file explains the purpose, key classes/functions, usage examples, design patterns, and best practices for that module.

## Quick Navigation

### Core Application

| Module | Purpose | Status |
|--------|---------|--------|
| [main.md](main.md) | Application entry point and CLI | ✅ Implemented |
| [config.md](config.md) | Configuration management (Singleton) | ✅ Implemented |
| [exceptions.md](exceptions.md) | Exception hierarchy | ✅ Implemented |
| [application.md](application.md) | Application bootstrap & DI | ✅ Implemented |
| [base_service.md](base_service.md) | Service infrastructure | ✅ Implemented |

### Functionality Modules

| Module | Purpose | Status |
|--------|---------|--------|
| [api.md](api.md) | REST API implementation | 🔄 Phase 3 |
| [security.md](security.md) | Encryption & key validation | 🔄 Phase 2 |
| [utils.md](utils.md) | Utility functions | 🔄 Phase 4 |

### Infrastructure

| Module | Purpose | Status |
|--------|---------|--------|
| [tests.md](tests.md) | Testing infrastructure | ✅ Phase 1 |
| [migrations.md](migrations.md) | Database migrations | 🔄 Phase 1 |
| [scripts.md](scripts.md) | Deployment & setup scripts | ✅ Phase 1 |

---

## Modules by Implementation Phase

### ✅ Phase 1: Project Setup (COMPLETE)
- **main.py**: Application entry point
- **config.py**: Configuration management
- **exceptions.py**: Exception hierarchy
- **application.py**: Application bootstrap & DI container
- **base_service.py**: Service infrastructure
- **tests/**: Testing infrastructure

### 🔄 Phase 2: Security & Encryption (UPCOMING)
- **app/security/encryption.py**: AES encryption/decryption
- **app/security/key_validator.py**: SSH key validation

### 🔄 Phase 3: REST API (UPCOMING)
- **app/api/routes.py**: API endpoints
- **app/api/schemas.py**: Pydantic request/response models
- **app/api/handlers.py**: Business logic handlers

### 🔄 Phase 4: Utilities (UPCOMING)
- **app/utils/ip_utils.py**: IP address utilities
- **app/utils/port_utils.py**: Port management utilities

---

## Documentation Structure

Each module documentation follows this structure:

### 1. **Purpose**
What the module does and why it exists.

### 2. **Module Structure**
Directory layout and file organization.

### 3. **Key Classes/Functions**
Main components with signatures and descriptions.

### 4. **Features**
Key capabilities and design patterns used.

### 5. **Usage Examples**
Practical examples showing how to use the module.

### 6. **Design Patterns**
Patterns applied (Singleton, Factory, Registry, etc.).

### 7. **Best Practices**
Guidelines for using the module correctly.

### 8. **Testing**
How to test the module.

### 9. **Troubleshooting**
Common issues and solutions.

### 10. **See Also**
Links to related documentation.

---

## Key Concepts by Module

### Configuration Management
See: [config.md](config.md)
- **Singleton Pattern**: Single configuration instance
- **Dataclass Pattern**: Type-safe configuration
- **Environment Variables**: Externalized configuration

### Exception Hierarchy  
See: [exceptions.md](exceptions.md)
- **Domain-Specific Exceptions**: Clear error types
- **Error Codes**: Programmatic error handling
- **Exception Chaining**: Preservation of context

### Application Bootstrap
See: [application.md](application.md)
- **Factory Pattern**: Clean object creation
- **Dependency Injection**: Loose coupling
- **Lifecycle Management**: Initialize/shutdown sequence
- **Service Registry**: Central service access

### Service Infrastructure
See: [base_service.md](base_service.md)
- **Template Method Pattern**: Consistent service interface
- **Abstract Base Class**: Enforce service contract
- **Health Checking**: Service status monitoring
- **Lifecycle Management**: Initialize/shutdown in order

### Security & Encryption
See: [security.md](security.md)
- **AES-256 Encryption**: Strong symmetric encryption
- **Key Derivation**: PBKDF2 for key strength
- **SSH Key Validation**: Format and type checking

### REST API
See: [api.md](api.md)
- **FastAPI Framework**: Modern async web framework
- **Pydantic Validation**: Automatic input validation
- **Error Handling**: Exception to HTTP response mapping

### Utilities
See: [utils.md](utils.md)
- **IP Address Management**: Validation and analysis
- **Port Assignment**: Finding available ports
- **Helper Functions**: Common operations

### Testing
See: [tests.md](tests.md)
- **Pytest Framework**: Clean test structure
- **Fixtures**: Reusable test setup
- **Markers**: Test organization and filtering
- **Mocking**: Dependency isolation

### Database Migrations
See: [migrations.md](migrations.md)
- **Version Control**: Track schema changes
- **Reversibility**: Backup and rollback capability
- **Idempotency**: Safe to run multiple times

### Deployment Scripts
See: [scripts.md](scripts.md)
- **Shell Scripts**: System-level operations
- **Docker**: Containerization
- **Automation**: Deployment automation

---

## Development Workflow

### 1. **Understand the Architecture**
   Start with [ARCHITECTURE.md](../ARCHITECTURE.md)

### 2. **Review Relevant Module**
   See corresponding .md file for details

### 3. **Check Usage Examples**
   Each module has practical examples

### 4. **Follow Best Practices**
   See "Best Practices" section in each module

### 5. **Write Tests**
   See [tests.md](tests.md) for testing guidelines

### 6. **Reference Developer Guide**
   See [../DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)

---

## SOLID Principles Across Modules

### Single Responsibility Principle
- `Logger`: Only logging
- `DependencyContainer`: Only dependency management
- `BaseService`: Only service lifecycle
- Each module has one clear purpose

### Open/Closed Principle
- Abstract base classes for extension
- Service registry for adding services
- Plugin patterns for customization

### Liskov Substitution Principle
- Services inherit from `BaseService`
- Loggers implement `ILogger`
- Containers implement `IDependencyContainer`

### Interface Segregation Principle
- `ILogger`: Only logging interface
- `IDependencyContainer`: Only container interface
- Clients depend on specific interfaces

### Dependency Inversion Principle
- Depend on abstractions (interfaces)
- Services injected via constructor
- DependencyContainer manages dependencies

---

## Design Patterns Used

| Pattern | Module | Purpose |
|---------|--------|---------|
| **Singleton** | config.py, application.py | Single instance across app |
| **Factory** | application.py | Clean object creation |
| **Registry** | application.py, base_service.py | Central service access |
| **Builder** | config.py | Configuration construction |
| **Template Method** | base_service.py | Service lifecycle template |
| **Dependency Injection** | application.py | Loose coupling |
| **Strategy** | (future) | Pluggable algorithms |
| **Observer** | (future) | Event handling |

---

## Common Operations

### Get Configuration
```python
from pyargus import AppConfig
config = AppConfig.get_instance()
```
See: [config.md](config.md)

### Access Application
```python
from pyargus import ApplicationFactory
app = ApplicationFactory.get_instance()
```
See: [application.md](application.md)

### Create Service
Inherit from `BaseService`
See: [base_service.md](base_service.md)

### Handle Errors
Use domain-specific exceptions
See: [exceptions.md](exceptions.md)

### Register Service
```python
app.container.register("service_name", service)
```
See: [application.md](application.md)

### Validate Data
Use Pydantic schemas in API
See: [api.md](api.md)

### Encrypt Data
Use security module functions
See: [security.md](security.md)

---

## Testing Your Code

```bash
# All tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_config.py::test_singleton
```

See: [tests.md](tests.md)

---

## Related Documentation

- **Main Architecture**: [../ARCHITECTURE.md](../ARCHITECTURE.md)
- **Developer Guide**: [../DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)
- **Implementation Plan**: [../IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md)
- **Completion Summary**: [../STEP1_COMPLETE.md](../STEP1_COMPLETE.md)

---

## Status Summary

- **Phase 1** ✅ Complete: Core infrastructure, configuration, exceptions, application, services, tests
- **Phase 2** 🔄 Upcoming: Security & encryption
- **Phase 3** 🔄 Upcoming: REST API
- **Phase 4** 🔄 Upcoming: Utilities
- **Phases 5-8** 🔄 Upcoming: Testing, security hardening, deployment, monitoring

---

## Getting Help

1. **Module-specific**: Read the corresponding .md file
2. **Architecture**: See ARCHITECTURE.md
3. **Examples**: Check "Usage Examples" section in module docs
4. **Development**: See DEVELOPER_GUIDE.md
5. **Testing**: See tests.md

---

Last Updated: February 13, 2026
PyArgus Version: 0.1.0
