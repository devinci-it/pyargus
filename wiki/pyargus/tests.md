# tests/ - Testing Infrastructure

Location: `/tests/`

## Purpose

Comprehensive test suite for PyArgus. Provides fixtures, helpers, and tests for all modules using pytest framework.

## Module Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_config.py           # Configuration tests
├── test_application.py      # Application bootstrap tests
├── test_base_service.py     # Service infrastructure tests
├── test_api/
│   ├── __init__.py
│   ├── test_routes.py       # API endpoint tests
│   ├── test_schemas.py      # Pydantic schema tests
│   └── test_handlers.py     # Handler business logic tests
├── test_security/
│   ├── __init__.py
│   ├── test_encryption.py   # Encryption/decryption tests
│   └── test_key_validator.py # Key validation tests
└── test_utils/
    ├── __init__.py
    ├── test_ip_utils.py     # IP utility tests
    └── test_port_utils.py   # Port utility tests
```

## conftest.py

Provides shared pytest fixtures and test utilities.

**Key Fixtures**:

```python
@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def test_config():
    """Create test configuration."""
    return AppConfig(app_name="PyArgus-Test", debug=True)

@pytest.fixture
def test_logger():
    """Create test logger."""
    return Logger("PyArgus-Test", "DEBUG")

@pytest.fixture
def test_app(test_config):
    """Create test application instance."""
    app = Application(test_config)
    app.initialize()
    yield app
    app.shutdown()

@pytest.fixture
def encryption_key():
    """Provide test encryption key."""
    return "test-encryption-key-32chars-long!"
```

## Test Organization

### Unit Tests
Tests for individual components in isolation.

```python
# tests/test_config.py

@pytest.mark.unit
def test_app_config_singleton():
    """Test AppConfig singleton pattern."""
    config1 = AppConfig.get_instance(app_name="Test1")
    config2 = AppConfig.get_instance()
    assert config1 is config2

@pytest.mark.unit
def test_app_config_validation():
    """Test AppConfig validates settings."""
    with pytest.raises(ValueError):
        SecurityConfig(encryption_key="", ssh_key_path="")
```

### Integration Tests
Tests for multiple components working together.

```python
# tests/test_application.py

@pytest.mark.integration
def test_application_initialization(test_app):
    """Test application initializes correctly."""
    assert test_app.is_initialized
    assert test_app.config is not None
    assert test_app.container is not None

@pytest.mark.integration
def test_services_registered(test_app):
    """Test core services are registered."""
    assert test_app.container.has("logger")
    assert test_app.container.has("config")
```

### Security Tests
Tests for security-critical functionality.

```python
# tests/test_security/test_encryption.py

@pytest.mark.security
def test_encryption_decryption(encryption_key):
    """Test key can be encrypted and decrypted."""
    original = "-----BEGIN RSA PRIVATE KEY-----\\nMIIE..."
    encrypted = encrypt_key(original, encryption_key)
    decrypted = decrypt_key(encrypted, encryption_key)
    assert decrypted == original

@pytest.mark.security
def test_encryption_different_keys(encryption_key):
    """Test different keys produce different results."""
    data = "secret"
    encrypted1 = encrypt_key(data, "key1")
    encrypted2 = encrypt_key(data, "key2")
    assert encrypted1 != encrypted2
```

### API Tests
Tests for REST endpoints.

```python
# tests/test_api/test_routes.py

from fastapi.testclient import TestClient
from pyargus.api import app

client = TestClient(app)

@pytest.mark.integration
def test_health_check():
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.integration
def test_register_client():
    """Test client registration."""
    response = client.post("/api/register", json={
        "hostname": "test.example.com",
        "ip_address": "192.168.1.1",
        "public_key": "ssh-rsa AAAA..."
    })
    assert response.status_code == 201
    assert response.json()["client_id"] is not None
```

## Running Tests

### All Tests
```bash
pytest
pytest -v  # Verbose
pytest -s  # Show print statements
```

### By Marker
```bash
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m security         # Security tests only
pytest -m "not slow"       # Skip slow tests
```

### By File/Function
```bash
pytest tests/test_config.py              # Specific file
pytest tests/test_config.py::test_singleton  # Specific test
pytest tests/test_api/                   # All API tests
```

### With Coverage
```bash
pytest --cov=app                         # Basic coverage
pytest --cov=app --cov-report=html       # HTML report
pytest --cov=app --cov-report=term-missing  # Show missing lines
```

### Parallel Execution
```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

## Best Practices

### 1. Use Descriptive Names
```python
# Good
def test_should_raise_validation_error_when_email_is_invalid():
    pass

# Bad
def test_email():
    pass
```

### 2. Use Fixtures
```python
def test_with_fixture(test_app, temp_dir):
    """Fixtures are injected automatically."""
    assert test_app is not None
    assert os.path.exists(temp_dir)
```

### 3. Use Markers
```python
@pytest.mark.unit
@pytest.mark.slow
def test_something_slow():
    pass
```

### 4. Arrange-Act-Assert Pattern
```python
def test_addition():
    # Arrange
    a, b = 2, 3
    
    # Act
    result = a + b
    
    # Assert
    assert result == 5
```

### 5. Parametrize Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("2+3", 5),
    ("5+1", 6),
    ("0+0", 0),
])
def test_calculator(input, expected):
    assert eval(input) == expected
```

### 6. Mock External Dependencies
```python
from unittest.mock import Mock, patch

@patch("app.database.connect")
def test_with_mock_database(mock_connect):
    mock_connect.return_value = Mock()
    # Test code
```

## Pytest Configuration (pytest.ini)

```ini
[pytest]
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

testpaths = tests
addopts = -v --strict-markers

markers =
    unit: Unit tests
    integration: Integration tests
    security: Security tests
    slow: Slow running tests
```

## Coverage Report

After running tests with coverage:

```bash
# Terminal report
pytest --cov=app --cov-report=term-missing

# HTML report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Target coverage
pytest --cov=app --cov-fail-under=80
```

## Example Test File

```python
# tests/test_my_module.py
import pytest
from pyargus.my_module import MyService
from pyargus import Logger

@pytest.fixture
def my_logger():
    return Logger("test")

@pytest.fixture
def my_service(my_logger):
    service = MyService(my_logger)
    service.initialize()
    yield service
    service.shutdown()

@pytest.mark.unit
def test_service_initialization(my_service):
    assert my_service.is_initialized

@pytest.mark.unit
def test_service_method(my_service):
    result = my_service.do_something()
    assert result is not None

@pytest.mark.security
def test_sensitive_operation_is_protected(my_service):
    # Test security
    pass

@pytest.mark.parametrize("input,expected", [
    (1, "one"),
    (2, "two"),
])
def test_with_parameters(input, expected):
    assert str(input) in expected
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
      - run: pytest --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Troubleshooting

### Fixture Not Found
```
fixture 'my_fixture' not found
```
**Solution**: Ensure fixture is defined in conftest.py and pytest can find it.

### Import Errors
```
ImportError: No module named 'app'
```
**Solution**: Run tests from project root: `pytest` not `pytest tests/`

### Async Test Issues
```
@pytest.mark.asyncio
async def test_async_function():
    result = await async_func()
    assert result is not None
```

## Status: Phases 5 & Ongoing

Testing infrastructure created in Phase 1. Tests added throughout implementation phases.

## See Also

- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md#phase-5-testing-week-3-4)
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md) - Testing patterns
