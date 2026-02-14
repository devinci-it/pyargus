# app/base_service.py - Service Infrastructure

Location: `/app/base_service.py`

## Purpose

Provides abstract base classes and infrastructure for implementing all application services. Ensures consistent lifecycle management, logging, and error handling across all service implementations.

## Key Classes

### BaseService (Abstract)
```python
class BaseService(ABC):
    def __init__(self, service_name: str, logger: ILogger):
        self._service_name = service_name
        self._logger = logger
        self._is_initialized = False
        self._metadata: Dict[str, Any] = {}
    
    def initialize(self) -> None: ...
    def shutdown(self) -> None: ...
    def health_check(self) -> Dict[str, Any]: ...
    def _ensure_initialized(self) -> None: ...
```

Abstract base class for all application services.

**Purpose**:
- Define common service interface
- Manage lifecycle (initialize/shutdown)
- Provide health checking
- Ensure consistent logging
- Enforce initialization checks

**Properties**:
- `service_name`: Unique name for service
- `is_initialized`: Whether service is ready
- `logger`: ILogger instance
- `_metadata`: Service metadata storage

**Methods**:

#### initialize()
Called when service is set up. Override in subclasses.

```python
def initialize(self):
    super().initialize()
    # Service-specific initialization
    logger.info("My service initialized")
```

#### shutdown()
Called when service is torn down. Override in subclasses.

```python
def shutdown(self):
    # Service-specific cleanup
    logger.info("My service cleaning up")
    super().shutdown()  # Call last
```

#### health_check()
Perform service health check. Override to add service-specific checks.

```python
def health_check(self) -> Dict[str, Any]:
    health = super().health_check()
    health["custom_status"] = self._check_something()
    return health
```

#### _ensure_initialized()
Verify service is initialized before use.

```python
def some_method(self):
    self._ensure_initialized()  # Raises if not initialized
    # Safe to proceed
```

### Service Implementation Example

```python
from pyargus.base_service import BaseService

class SSHManager(BaseService):
    """Manages SSH operations."""
    
    def __init__(self, logger):
        super().__init__("SSHManager", logger)
        self._ssh_config = None
    
    def initialize(self):
        super().initialize()
        self.logger.info("Loading SSH configuration...")
        self._ssh_config = load_ssh_config()
        self.logger.info("SSH configuration loaded")
    
    def shutdown(self):
        self.logger.info("Closing SSH connections...")
        if self._ssh_config:
            self._ssh_config.close()
        super().shutdown()
    
    def add_key(self, key_path):
        self._ensure_initialized()
        # Safe to use SSH
        self._ssh_config.add_key(key_path)
    
    def health_check(self):
        health = super().health_check()
        health["ssh_keys_loaded"] = bool(self._ssh_config)
        return health
```

### ServiceRegistry
```python
class ServiceRegistry:
    def __init__(self, logger: ILogger):
        self._services: Dict[str, BaseService] = {}
        self._logger = logger
    
    def register(self, service: BaseService) -> None: ...
    def get(self, service_name: str) -> BaseService: ...
    def initialize_all(self) -> None: ...
    def shutdown_all(self) -> None: ...
    def health_check_all(self) -> Dict[str, Dict[str, Any]]: ...
```

Registry for managing multiple services.

**Purpose**:
- Central service management
- Lifecycle coordination
- Health monitoring
- Centralized initialization/shutdown

**Methods**:

#### register(service)
Register a service in the registry.

```python
registry = ServiceRegistry(logger)
ssh_manager = SSHManager(logger)
registry.register(ssh_manager)
```

#### get(service_name)
Retrieve registered service by name.

```python
ssh_manager = registry.get("SSHManager")
ssh_manager.add_key("/path/to/key")
```

#### initialize_all()
Initialize all registered services in order.

```python
registry.initialize_all()  # All services ready
```

#### shutdown_all()
Shutdown all services in reverse order (LIFO).

```python
registry.shutdown_all()  # Clean shutdown
```

#### health_check_all()
Check health of all services.

```python
health = registry.health_check_all()
# Returns: {
#     "ServiceName": {"status": "healthy", ...},
#     "OtherService": {"status": "unhealthy", ...}
# }
```

## Service Lifecycle

```
Service Created
  ↓
register(service)
  ↓
initialize_all() or initialize()
  ├─ Service performs setup
  ├─ Loads resources
  └─ Sets _is_initialized = True
  ↓
Service Ready
  ├─ Can call all methods
  ├─ health_check() returns healthy
  └─ Other services can use it
  ↓
shutdown_all() or shutdown()
  ├─ Service performs cleanup
  ├─ Closes connections
  ├─ Releases resources
  └─ Sets _is_initialized = False
  ↓
Service Stopped
```

## Usage Examples

### Implementing a Service

```python
from pyargus.base_service import BaseService
from pyargus import Logger

class DatabaseService(BaseService):
    def __init__(self, logger, connection_string):
        super().__init__("DatabaseService", logger)
        self.connection_string = connection_string
        self.connection = None
    
    def initialize(self):
        super().initialize()
        self.logger.info(f"Connecting to {self.connection_string}...")
        try:
            self.connection = connect(self.connection_string)
            self.logger.info("Database connection established")
        except Exception as e:
            self.logger.error("Failed to connect to database", e)
            raise
    
    def shutdown(self):
        if self.connection:
            self.logger.info("Closing database connection...")
            self.connection.close()
        super().shutdown()
    
    def health_check(self):
        health = super().health_check()
        try:
            # Test connection
            self.connection.ping()
            health["database_connection"] = "ok"
        except Exception as e:
            health["database_connection"] = f"error: {str(e)}"
        return health
    
    def query(self, sql):
        self._ensure_initialized()
        return self.connection.execute(sql)
```

### Using ServiceRegistry

```python
from pyargus.base_service import ServiceRegistry
from pyargus import Logger

logger = Logger("app", "INFO")
registry = ServiceRegistry(logger)

# Create and register services
db_service = DatabaseService(logger, "sqlite:///app.db")
registry.register(db_service)

ssh_service = SSHManager(logger)
registry.register(ssh_service)

# Initialize all at once
registry.initialize_all()

# Use services
results = db_service.query("SELECT * FROM clients")

# Check health
health = registry.health_check_all()
print(health)

# Shutdown properly
registry.shutdown_all()
```

### Metadata Storage

```python
service = MyService(logger)

# Store metadata
service.set_metadata("version", "1.0")
service.set_metadata("author", "PyArgus")

# Retrieve metadata
version = service.get_metadata("version")
author = service.get_metadata("author", "Unknown")
```

## Design Patterns

### Template Method Pattern
- `initialize()` and `shutdown()` define lifecycle steps
- Subclasses override specific steps
- Base class manages sequence

### Abstract Base Class Pattern
- Forces subclasses to implement required methods
- Provides default implementations
- Ensures consistent interface

### Registry Pattern
- ServiceRegistry centrally manages services
- Easy lookup by name
- Bulk operations (initialize_all, shutdown_all)

## Best Practices

1. **Always call super()**: Call parent initialize/shutdown
2. **Check initialization**: Use `_ensure_initialized()` in methods
3. **Log activities**: Log initialization and shutdown
4. **Handle errors**: Catch and log errors gracefully
5. **Implement health_check**: Report service status
6. **Clean resources**: Close connections in shutdown()
7. **Use metadata**: Store service info via metadata API
8. **Register early**: Register all services before initializing

## Error Handling

```python
class MyService(BaseService):
    def initialize(self):
        super().initialize()
        try:
            self._setup_resources()
        except Exception as e:
            self.logger.error("Failed to initialize", e)
            raise    # Propagate to caller

    def some_method(self):
        try:
            self._ensure_initialized()
        except PyArgusException as e:
            self.logger.error(f"Service not ready: {e.message}")
            raise
```

## Testing

```python
import pytest
from pyargus.base_service import BaseService
from pyargus import Logger

class TestService(BaseService):
    def __init__(self, logger):
        super().__init__("TestService", logger)

def test_service_lifecycle():
    logger = Logger("test")
    service = TestService(logger)
    
    assert not service.is_initialized
    
    service.initialize()
    assert service.is_initialized
    
    service.shutdown()
    assert not service.is_initialized

def test_ensure_initialized():
    logger = Logger("test")
    service = TestService(logger)
    
    with pytest.raises(PyArgusException):
        service._ensure_initialized()
    
    service.initialize()
    service._ensure_initialized()  # OK
```

## See Also

- [ARCHITECTURE.md](../ARCHITECTURE.md#4-base-service-infrastructure-appbase_servicepy)
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md#adding-a-new-service)
- [application.md](application.md) - Uses services via DependencyContainer
