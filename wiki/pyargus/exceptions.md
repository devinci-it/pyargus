# app/exceptions.py - Exception Hierarchy

Location: `/app/exceptions.py`

## Purpose

Defines domain-specific exception classes for the PyArgus application. Provides a clear exception hierarchy for better error handling, debugging, and programmatic error detection.

## Exception Hierarchy

```
Exception
└── PyArgusException (base class)
    ├── ConfigurationError
    ├── DatabaseError
    ├── ValidationError
    ├── AuthenticationError
    ├── AuthorizationError
    ├── SSHError
    ├── EncryptionError
    ├── ResourceNotFoundError
    └── ResourceConflictError
```

## Base Exception

### PyArgusException
```python
class PyArgusException(Exception):
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
```

Base exception for all PyArgus-specific errors. Includes:
- **message**: Descriptive error message
- **error_code**: Unique code for programmatic handling

**Usage**:
```python
from pyargus import PyArgusException

try:
    # Something went wrong
    raise PyArgusException("Custom error", error_code="CUSTOM_ERROR")
except PyArgusException as e:
    print(f"Error: {e.message} ({e.error_code})")
```

## Specific Exceptions

### ConfigurationError
```python
ConfigurationError(message: str)
```

Raised when application configuration is invalid or incomplete.

**Example**:
```python
from pyargus import ConfigurationError

if not os.environ.get("ENCRYPTION_KEY"):
    raise ConfigurationError("ENCRYPTION_KEY must be set in environment")
```

### DatabaseError
```python
DatabaseError(message: str)
```

Raised when database operations fail.

**Example**:
```python
from pyargus import DatabaseError

try:
    db.save(record)
except Exception as e:
    raise DatabaseError(f"Failed to save record: {str(e)}")
```

### ValidationError
```python
ValidationError(message: str, field: str = None)
```

Raised when data validation fails. Optionally tracks which field failed.

**Example**:
```python
from pyargus import ValidationError

def validate_email(email: str):
    if "@" not in email:
        raise ValidationError("Invalid email format", field="email")
```

### AuthenticationError
```python
AuthenticationError(message: str = "Authentication failed")
```

Raised when authentication fails (invalid credentials, expired tokens, etc.).

**Example**:
```python
from pyargus import AuthenticationError

def verify_client(client_id: str, credentials: str):
    if not is_valid(credentials):
        raise AuthenticationError("Invalid credentials for client")
```

### AuthorizationError
```python
AuthorizationError(message: str = "Authorization failed")
```

Raised when user lacks required permissions/authorization.

**Example**:
```python
from pyargus import AuthorizationError

def delete_client(client_id: str, user_id: str):
    if not is_admin(user_id):
        raise AuthorizationError("Only admins can delete clients")
```

### SSHError
```python
SSHError(message: str)
```

Raised when SSH operations fail (key loading, connection errors, etc.).

**Example**:
```python
from pyargus import SSHError

try:
    ssh_manager.load_key(key_path)
except Exception as e:
    raise SSHError(f"Failed to load SSH key: {str(e)}")
```

### EncryptionError
```python
EncryptionError(message: str)
```

Raised when encryption/decryption operations fail.

**Example**:
```python
from pyargus import EncryptionError

try:
    decrypted = decrypt_key(encrypted_data, key)
except Exception as e:
    raise EncryptionError(f"Failed to decrypt: {str(e)}")
```

### ResourceNotFoundError
```python
ResourceNotFoundError(resource_type: str, resource_id: str)
```

Raised when a requested resource is not found.

**Example**:
```python
from pyargus import ResourceNotFoundError

def get_client(client_id: str):
    client = db.get_client_by_id(client_id)
    if not client:
        raise ResourceNotFoundError("Client", client_id)
    return client
```

### ResourceConflictError
```python
ResourceConflictError(resource_type: str, resource_identifier: str)
```

Raised when a resource already exists (duplicate, conflict, etc.).

**Example**:
```python
from pyargus import ResourceConflictError

def register_client(hostname: str):
    if db.client_exists(hostname):
        raise ResourceConflictError("Client", hostname)
    return db.create_client(hostname)
```

## Usage Patterns

### Basic Exception Handling
```python
from pyargus import PyArgusException, ConfigurationError

try:
    # Do something
    result = do_work()
except ConfigurationError as e:
    print(f"Configuration error: {e.message}")
except PyArgusException as e:
    print(f"General error: {e.message} ({e.error_code})")
```

### Specific Error Detection
```python
from pyargus import ResourceNotFoundError, AuthenticationError

try:
    user = get_user(user_id)
except ResourceNotFoundError as e:
    # Handle missing user
    return 404, f"User not found: {e.message}"
except AuthenticationError as e:
    # Handle auth failure
    return 401, f"Authentication failed: {e.message}"
```

### Re-raising with Context
```python
from pyargus import DatabaseError, ValidationError

try:
    validate_data(data)
except ValidationError as e:
    # Add context and re-raise
    raise DatabaseError(f"Cannot save invalid data: {e.message}")
```

### Logging Errors
```python
from pyargus import PyArgusException
from pyargus import Logger

logger = Logger(__name__)

try:
    risky_operation()
except PyArgusException as e:
    logger.error(f"Operation failed: {e.message}", exception=e)
    # Handle gracefully
```

## Design Benefits

### Clear Intent
Each exception type clearly indicates what went wrong:
```python
# Immediately clear what failed
except ValidationError as e:    # Data validation
except SSHError as e:           # SSH operation
except DatabaseError as e:      # Database operation
except ConfigurationError as e: # Configuration issue
```

### Programmatic Handling
Error codes enable programmatic handling:
```python
except PyArgusException as e:
    if e.error_code == "VALIDATION_ERROR":
        # Handle validation
    elif e.error_code == "NOT_FOUND":
        # Handle missing resource
    elif e.error_code == "CONFLICT":
        # Handle duplicate
```

### API Responses
Easily convert to HTTP responses:
```python
from pyargus import PyArgusException

try:
    result = register_client(request_data)
except ResourceConflictError as e:
    return {"error": e.message}, 409
except ValidationError as e:
    return {"error": e.message, "field": e.field}, 400
except PyArgusException as e:
    return {"error": e.message, "code": e.error_code}, 500
```

### Testing
Specific exceptions make tests clearer:
```python
import pytest
from pyargus import ResourceNotFoundError, ValidationError

def test_missing_client():
    with pytest.raises(ResourceNotFoundError):
        get_client("nonexistent")

def test_invalid_email():
    with pytest.raises(ValidationError) as exc_info:
        validate_email("invalid")
    assert exc_info.value.field == "email"
```

## Best Practices

1. **Raise specific exceptions**: Use most specific exception type
2. **Include context**: Provide clear error messages
3. **Preserve original**: Consider wrapping original exception
4. **Log appropriately**: Use correct log level for each exception
5. **Handle early**: Catch specific exceptions early
6. **Document in functions**: Specify which exceptions are raised
7. **Use error codes**: Help with programmatic error handling

## Example: Complete Error Handling

```python
from pyargus import (
    ValidationError,
    AuthenticationError,
    ResourceNotFoundError,
    SSHError,
    PyArgusException
)

def register_client(hostname: str, public_key: str) -> dict:
    """
    Register a new client.
    
    Args:
        hostname: Client hostname
        public_key: SSH public key
    
    Returns:
        Client registration details
    
    Raises:
        ValidationError: If hostname or key invalid
        ResourceConflictError: If client already exists
        SSHError: If key validation fails
    """
    # Validate input
    if not hostname:
        raise ValidationError("Hostname required", field="hostname")
    if not public_key:
        raise ValidationError("Public key required", field="public_key")
    
    # Check if exists
    if db.client_exists(hostname):
        raise ResourceConflictError("Client", hostname)
    
    # Validate SSH key
    try:
        validate_ssh_key(public_key)
    except Exception as e:
        raise SSHError(f"Invalid SSH key: {str(e)}")
    
    # Register
    client = db.create_client(hostname, public_key)
    return {"client_id": client.id, "hostname": client.hostname}
```

## See Also

- [ARCHITECTURE.md](../ARCHITECTURE.md#2-exception-hierarchy-appexceptionspy)
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md#exception-handling-patterns)
- [application.py](application.md) - Uses exceptions in Application class
