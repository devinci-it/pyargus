# app/application.py - Application Bootstrap & Dependency Injection

Location: `/app/application.py`

## Purpose

Provides the main application bootstrap class and dependency injection container. Serves as the central orchestrator for application lifecycle, component initialization, and service management.

## Key Classes

### ILogger (Interface)
```python
class ILogger(ABC):
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None: ...
    @abstractmethod
    def info(self, message: str, **kwargs) -> None: ...
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None: ...
    @abstractmethod
    def error(self, message: str, exception: Exception = None, **kwargs) -> None: ...
```

Abstract interface for logging. Allows swapping logger implementations.

### Logger (Implementation)
```python
class Logger(ILogger):
    def __init__(self, name: str, level: str = "INFO"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper()))
        # Install handler...
    
    def debug(self, message: str, **kwargs) -> None: ...
    def info(self, message: str, **kwargs) -> None: ...
    def warning(self, message: str, **kwargs) -> None: ...
    def error(self, message: str, exception: Exception = None, **kwargs) -> None: ...
```

Concrete logger implementation wrapping Python's logging module.

**Usage**:
```python
from pyargus import Logger

logger = Logger("my_module", "DEBUG")
logger.info("Application started")
logger.error("Something failed", exception=e)
```

### IDependencyContainer (Interface)
```python
class IDependencyContainer(ABC):
    @abstractmethod
    def get(self, service_name: str): ...
    @abstractmethod
    def register(self, service_name: str, instance) -> None: ...
```

Abstract interface for dependency injection container.

### DependencyContainer (Implementation)
```python
class DependencyContainer(IDependencyContainer):
    def __init__(self):
        self._services = {}
        self._logger = logging.getLogger(__name__)
    
    def register(self, service_name: str, instance) -> None: ...
    def get(self, service_name: str): ...
    def has(self, service_name: str) -> bool: ...
```

Service registry implementing the Registry pattern for dependency management.

**Features**:
- Register services for later retrieval
- Singleton pattern for service instances
- Exception on duplicate registration
- Exception on missing service

**Usage**:
```python
from pyargus import DependencyContainer, Logger

container = DependencyContainer()

# Register services
logger = Logger("app")
container.register("logger", logger)

# Retrieve services
logger = container.get("logger")

# Check if registered
if container.has("logger"):
    logger = container.get("logger")
```

### Application (Main Class)
```python
class Application:
    def __init__(self, config: Optional[AppConfig] = None):
        self._config = config or AppConfig.from_env()
        self._container = DependencyContainer()
        self._logger = Logger(...)
        self._is_initialized = False
    
    def initialize(self) -> "Application": ...
    def shutdown(self) -> None: ...
    
    @property
    def config(self) -> AppConfig: ...
    @property
    def container(self) -> IDependencyContainer: ...
    @property
    def logger(self) -> ILogger: ...
    @property
    def is_initialized(self) -> bool: ...
```

Main application orchestrator. Coordinates:
- Configuration loading and validation
- Dependency container setup
- Component initialization
- Application lifecycle

**Workflow**:
1. Create instance with optional config
2. Call `initialize()` to setup components
3. Use `container` to access services
4. Call `shutdown()` for cleanup

**Example**:
```python
from pyargus import Application, AppConfig

# Create with custom config
config = AppConfig(app_name="MyApp")
app = Application(config)

# Initialize
app.initialize()

# Use
logger = app.logger
config = app.config

# Shutdown
app.shutdown()
```

### ApplicationFactory
```python
class ApplicationFactory:
    _instance: Optional[Application] = None
    
    @classmethod
    def create(cls, config: Optional[AppConfig] = None) -> Application: ...
    @classmethod
    def get_instance(cls) -> Optional[Application]: ...
    @classmethod
    def set_instance(cls, app: Application) -> None: ...
```

Factory for creating and managing Application instances using Factory and Singleton patterns.

**Usage**:
```python
from pyargus import ApplicationFactory

# Create and initialize
app = ApplicationFactory.create()
ApplicationFactory.set_instance(app)

# Get instance later
app = ApplicationFactory.get_instance()
if app:
    config = app.config
    logger = app.logger
```

## Initialization Flow

```
Application.__init__()
  ↓
_validate_configuration()
  ├─ Check encryption key
  ├─ Check SSH key path
  └─ Log validation result
  ↓
[Ready to initialize]
  ↓
Application.initialize()
  ├─ _register_core_services()
  │   ├─ Register: config
  │   ├─ Register: logger
  │   └─ Register: container
  ├─ _initialize_components()
  │   ├─ (Database - future)
  │   ├─ (API - future)
  │   ├─ (SSH Manager - future)
  │   └─ (Other services - future)
  └─ Set _is_initialized = True
  ↓
[Application ready]
```

## Usage Examples

### Basic Application Setup
```python
from pyargus import ApplicationFactory

# Create application
app = ApplicationFactory.create()

# Access components
logger = app.logger
container = app.container
config = app.config

# Use services
logger.info(f"App: {config.app_name}")
logger.info(f"Port: {config.api.port}")
```

### Custom Configuration
```python
from pyargus import Application, AppConfig

config = AppConfig(
    app_name="PyArgus",
    environment="production",
    debug=False
)

app = Application(config)
app.initialize()

# Now ready to use
```

### With Context Manager (Testing)
```python
def test_with_app():
    app = ApplicationFactory.create()
    try:
        logger = app.logger
        assert app.is_initialized
    finally:
        app.shutdown()
```

### Accessing Core Services
```python
app = ApplicationFactory.create()

# All core services available after initialization
logger = app.container.get("logger")      # ILogger
config = app.container.get("config")      # AppConfig
container = app.container.get("container") # IDependencyContainer

# Use logger
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message", exception=e)
```

## Design Patterns

### Singleton Pattern
- ApplicationFactory.get_instance() returns same Application
- Application maintains single DependencyContainer
- Single configuration instance

### Factory Pattern
- ApplicationFactory.create() hides Application creation details
- Clean interface for application bootstrapping

### Registry Pattern
- DependencyContainer registers services
- Services retrieved by name
- Prevents hard-coded dependencies

### Dependency Injection
- Services injected via constructor
- DependencyContainer manages instances
- Enables loose coupling

### Template Method Pattern
- `initialize()` defines sequence
- Subclasses override specific steps
- `_register_core_services()` can be extended

## Best Practices

1. **Create once**: ApplicationFactory ensures single instance
2. **Initialize before use**: Always call `initialize()`
3. **Store instance**: Use `ApplicationFactory.set_instance()`
4. **Access via container**: Get services from container
5. **Handle shutdown**: Call `shutdown()` for cleanup
6. **Use logger**: All components should use injected logger
7. **Configure validation**: Configuration validates on creation

## Error Handling

```python
from pyargus import Application, ConfigurationError

try:
    app = Application()
    app.initialize()
except ConfigurationError as e:
    print(f"Configuration error: {e.message}")
    sys.exit(1)
except Exception as e:
    print(f"Initialization failed: {e}")
    sys.exit(1)

# Application ready
```

## Testing

```python
import pytest
from pyargus import Application, ApplicationFactory

@pytest.fixture
def test_app():
    """Provide test application instance."""
    app = ApplicationFactory.create()
    yield app
    app.shutdown()

def test_app_initialization(test_app):
    assert test_app.is_initialized
    assert test_app.config is not None
    assert test_app.container is not None

def test_app_services(test_app):
    logger = test_app.container.get("logger")
    config = test_app.container.get("config")
    assert logger is not None
    assert config is not None
```

## See Also

- [ARCHITECTURE.md](../ARCHITECTURE.md#3-application-bootstrap-appapplicationpy)
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md#dependency-injection-pattern)
- [config.md](config.md) - Configuration management
- [base_service.md](base_service.md) - Service infrastructure
- [main.py](main.md) - Uses Application for initialization
