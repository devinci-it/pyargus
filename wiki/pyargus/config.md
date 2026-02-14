# app/config.py - Configuration Management

Location: `/app/config.py`

## Purpose

Centralized configuration management for the PyArgus application using the **Singleton pattern**. Provides type-safe, validated configuration that loads from dataclasses and environment variables.

## Key Classes

### DatabaseConfig
```python
@dataclass
class DatabaseConfig:
    database_url: str
    echo: bool = False
    timeout: int = 30
```

Database connection settings including:
- **database_url**: Connection string (SQLite, PostgreSQL, etc.)
- **echo**: Enable SQL query logging
- **timeout**: Connection timeout in seconds

### APIConfig
```python
@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 4
```

API server settings:
- **host**: Bind address
- **port**: Server port (0-65535)
- **debug**: Debug mode flag
- **reload**: Auto-reload on code changes
- **workers**: Number of worker processes

### SecurityConfig
```python
@dataclass
class SecurityConfig:
    encryption_key: str
    ssh_key_path: str
    authorized_keys_path: Optional[str] = None
    default_port_start: int = 9221
    default_port_end: int = 9999
```

Security and encryption settings:
- **encryption_key**: AES encryption key (REQUIRED)
- **ssh_key_path**: Path to SSH key (REQUIRED)
- **authorized_keys_path**: Path to authorized_keys file
- **default_port_start/end**: SSH tunnel port range

### AppConfig (Singleton)
```python
@dataclass
class AppConfig:
    app_name: str = "PyArgus"
    version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    
    database: DatabaseConfig
    api: APIConfig
    security: SecurityConfig
```

Main application configuration with nested configs.

## Features

### Singleton Pattern

```python
# Get or create singleton instance
config = AppConfig.get_instance()

# Same instance every time
config2 = AppConfig.get_instance()
assert config is config2  # True
```

### Environment Variable Loading

```python
import os

os.environ["APP_NAME"] = "MyApp"
os.environ["DEBUG"] = "true"
os.environ["API_PORT"] = "9000"

config = AppConfig.from_env()
assert config.app_name == "MyApp"
assert config.debug is True
assert config.api.port == 9000
```

### Automatic Validation

Configuration validates on initialization:

```python
# Valid
config = DatabaseConfig(database_url="sqlite:///app.db")

# Invalid - raises ValueError
config = DatabaseConfig(database_url="")
```

## Usage Examples

### Basic Usage
```python
from app import AppConfig

config = AppConfig.get_instance()

# Access nested settings
print(config.api.port)           # 8000
print(config.database.database_url)  # sqlite:///pyargus.db
print(config.security.encryption_key)
```

### Load from Environment
```python
from app import AppConfig
import os

# Set environment variables
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/pyargus"
os.environ["API_PORT"] = "9000"
os.environ["ENCRYPTION_KEY"] = "my-secret-key"
os.environ["SSH_KEY_PATH"] = "/home/user/.ssh/id_rsa"

# Load from environment
config = AppConfig.from_env()
```

### Custom Configuration
```python
from app import AppConfig, DatabaseConfig, APIConfig, SecurityConfig

config = AppConfig(
    app_name="PyArgus-Custom",
    environment="production",
    debug=False,
    database=DatabaseConfig(database_url="postgresql://..."),
    api=APIConfig(port=8080, workers=8),
    security=SecurityConfig(
        encryption_key="prod-key",
        ssh_key_path="/etc/pyargus/ssh_key"
    )
)
```

### Reset Singleton (Testing)
```python
from app import AppConfig

# Reset for clean state
AppConfig.reset_instance()

# Create new instance
config = AppConfig.get_instance()
```

## Design Patterns

### Singleton Pattern
- Single instance across entire application
- Prevents multiple configuration objects
- All components access same config

### Dataclass Pattern
- Type-safe configuration
- Default values
- Automatic `__init__`, `__repr__`
- Easy validation in `__post_init__`

### Builder Pattern (via Environment)
- `from_env()` constructs from environment variables
- Separates configuration concerns
- Works with environment-specific settings

## Environment Variables

### Required
```bash
ENCRYPTION_KEY=your-secret-key
SSH_KEY_PATH=/path/to/ssh/key
```

### Optional
```bash
APP_NAME=PyArgus
APP_VERSION=0.1.0
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_RELOAD=true
API_WORKERS=4

DATABASE_URL=sqlite:///pyargus.db
DATABASE_ECHO=false

AUTHORIZED_KEYS_PATH=~/.ssh/authorized_keys
DEFAULT_PORT_START=9221
DEFAULT_PORT_END=9999
```

## Best Practices

1. **Use singleton**: Always get instance via `AppConfig.get_instance()`
2. **Load from env**: Use `AppConfig.from_env()` in production
3. **Validate early**: Configuration validates on creation
4. **Document vars**: Keep `.env.example` updated
5. **Type hints**: All config attributes are type-hinted
6. **Nested structure**: Group related config in sub-configs

## Testing

```python
import pytest
from app import AppConfig

@pytest.fixture
def test_config():
    """Create isolated test configuration."""
    AppConfig.reset_instance()
    config = AppConfig(
        app_name="PyArgus-Test",
        environment="test"
    )
    yield config
    AppConfig.reset_instance()

def test_config_values(test_config):
    assert test_config.app_name == "PyArgus-Test"
    assert test_config.environment == "test"
```

## See Also

- [ARCHITECTURE.md](../ARCHITECTURE.md#1-configuration-management-appconfigpy)
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md#configuration-patterns)
- [main.py](main.md) - Uses config for initialization
