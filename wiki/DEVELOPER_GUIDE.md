# PyArgus Developer Quick Reference

## Project Layout at a Glance

```
pyargus/
├── main.py                 ← Start here: application entry point
├── requirements.txt        ← Install: pip install -r requirements.txt
├── .env.example            ← Copy and customize
├── app/
│   ├── __init__.py         ← Public API exports
│   ├── config.py           ← Configuration (Singleton)
│   ├── exceptions.py       ← Domain exceptions
│   ├── application.py      ← Bootstrap & DI container
│   ├── base_service.py     ← Service template
│   ├── api/                ← REST endpoints (Phase 3)
│   ├── security/           ← Encryption (Phase 2)
│   └── utils/              ← Helpers (Phase 4)
├── tests/                  ← Pytest tests
├── migrations/             ← Database migrations (Phase 1)
└── scripts/                ← Deployment scripts
```

## Common Tasks

### Running the Application
```bash
python main.py                      # Start normally
python main.py --debug              # Debug mode
python main.py --port 9000          # Custom port
python main.py --environment prod   # Production
```

### Running Tests
```bash
pytest                              # Run all
pytest -v                           # Verbose
pytest --cov=app                    # With coverage
pytest tests/test_config.py         # Specific file
pytest -m unit                      # By marker
pytest -x                           # Stop on first failure
```

### Code Quality
```bash
black app/ tests/                   # Format code
flake8 app/ tests/                  # Lint
mypy app/ tests/                    # Type check
isort app/ tests/                   # Sort imports
```

### Debugging
```python
# Use the logger
from pyargus import Application

app = ApplicationFactory.create()
logger = app.logger

logger.debug("Debug message")     # Won't show unless LOG_LEVEL=DEBUG
logger.info("Info message")
logger.warning("Warning!")
logger.error("Error!", exception)
```

## Adding a New Service

### Step 1: Create service module
```python
# app/my_service.py
from pyargus.base_service import BaseService

class MyService(BaseService):
    def __init__(self, logger):
        super().__init__("MyService", logger)
    
    def initialize(self):
        super().initialize()
        self.logger.info("Setting up...")
    
    def shutdown(self):
        self.logger.info("Cleaning up...")
        super().shutdown()
    
    def my_method(self):
        self._ensure_initialized()
        # Implementation
```

### Step 2: Register in Application
```python
# In app/application.py _register_core_services()
my_service = MyService(self._logger)
self._container.register("my_service", my_service)
```

### Step 3: Use in code
```python
from pyargus import ApplicationFactory

app = ApplicationFactory.get_instance()
my_service = app.container.get("my_service")
my_service.my_method()
```

## Adding a New API Endpoint

### Step 1: Create schema
```python
# app/api/schemas.py
from pydantic import BaseModel

class MyRequest(BaseModel):
    name: str
    value: int

class MyResponse(BaseModel):
    status: str
    id: int
```

### Step 2: Create handler
```python
# app/api/handlers.py
def handle_my_action(request: MyRequest):
    # Business logic
    return MyResponse(status="ok", id=1)
```

### Step 3: Add route
```python
# app/api/routes.py
@router.post("/my-endpoint")
def my_endpoint(request: MyRequest):
    return handle_my_action(request)
```

## Exception Handling Patterns

### Raise specific exceptions
```python
from pyargus import ValidationError, ResourceNotFoundError

# Data validation
if not email:
    raise ValidationError("Email required", field="email")

# Resource not found
if not client:
    raise ResourceNotFoundError("Client", client_id)
```

### Handle exceptions
```python
from pyargus import PyArgusException

try:
    # Code
    pass
except ValidationError as e:
    logger.warning(f"Validation failed: {e.message}")
except PyArgusException as e:
    logger.error(f"Error [{e.error_code}]: {e.message}")
```

## Configuration Patterns

### Access configuration
```python
from pyargus import AppConfig, ApplicationFactory

# As singleton
config = AppConfig.get_instance()
print(config.api.port)

# Via application
app = ApplicationFactory.get_instance()
config = app.config
```

### From environment
```python
import os
from pyargus import AppConfig

# Set env variables
os.environ["API_PORT"] = "9000"
os.environ["DEBUG"] = "true"

# Load
config = AppConfig.from_env()
```

## Dependency Injection Pattern

### Register service
```python
container = app.container
container.register("my_service", my_service_instance)
```

### Get service
```python
my_service = container.get("my_service")
```

### In constructor
```python
class MyHandler:
    def __init__(self, container):
        self.logger = container.get("logger")
        self.config = container.get("config")
```

## Logging Best Practices

```python
logger.debug("Entering function")          # Detailed flow
logger.info("User registered")              # Important events
logger.warning("Deprecated function used")  # Potential issues
logger.error("Database connection failed", exception)  # Errors
```

## Testing Patterns

### Unit test
```python
@pytest.mark.unit
def test_something():
    assert len([]) == 0
```

### With fixtures
```python
def test_with_app(test_app):
    logger = test_app.logger
    logger.info("Test info")
```

### Mocking services
```python
from unittest.mock import Mock

mock_logger = Mock()
my_service = MyService(mock_logger)
```

## Common Errors & Solutions

### "Service not registered"
```python
# Wrong: Getting before registering
service = container.get("my_service")  # Error!

# Right: Check if registered
if container.has("my_service"):
    service = container.get("my_service")
```

### "Service not initialized"
```python
# Wrong: Using before initialization
service.do_something()  # Error!

# Right: Check initialization
if service.is_initialized:
    service.do_something()
```

### Configuration validation fails
Fix in `.env`:
```bash
# Must set encryption key
ENCRYPTION_KEY=your-secret-key-here

# Must set SSH key path
SSH_KEY_PATH=/path/to/ssh/key
```

## Environment Variables Quick Reference

```bash
# Core
APP_NAME=PyArgus
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///pyargus.db

# Security (REQUIRED)
ENCRYPTION_KEY=your-secret-key
SSH_KEY_PATH=/home/user/.ssh/id_rsa

# Optional
API_WORKERS=4
DEFAULT_PORT_START=9221
DEFAULT_PORT_END=9999
```

## Resources

- [ARCHITECTURE.md](ARCHITECTURE.md) - Full architecture guide
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Development plan
- [STEP1_COMPLETE.md](STEP1_COMPLETE.md) - Step 1 details
- Code: See inline docstrings in source files

## Support

When stuck:
1. Check ARCHITECTURE.md for patterns
2. Look at existing code for examples
3. Run tests to understand expected behavior
4. Check exception messages for guidance
