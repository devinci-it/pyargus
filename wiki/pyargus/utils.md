# app/utils/ - Utility Modules

Location: `/app/utils/`

## Purpose

Contains reusable utility functions and helper classes for common operations across the application. Provides IP address management, port assignment, and other utility functions.

## Module Structure

```
app/utils/
├── __init__.py          # Package initialization
├── ip_utils.py          # IP address utilities (Phase 4)
└── port_utils.py        # Port management utilities (Phase 4)
```

## Planned Components

### ip_utils.py
IP address validation and utilities.

**Planned Functions**:

```python
import ipaddress
from typing import Optional

def validate_ip_address(ip_string: str) -> bool:
    """
    Validate IPv4 or IPv6 address format.
    
    Args:
        ip_string: IP address to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False

def is_private_ip(ip_string: str) -> bool:
    """
    Check if IP address is private (RFC 1918).
    
    Args:
        ip_string: IP address to check
    
    Returns:
        True if private, False if public
    """
    try:
        ip = ipaddress.ip_address(ip_string)
        return ip.is_private
    except ValueError:
        raise ValidationError("Invalid IP address", field="ip_address")

def get_client_ip_address(request) -> Optional[str]:
    """
    Extract client IP address from HTTP request.
    
    Checks X-Forwarded-For and other headers for proxy scenarios.
    
    Args:
        request: HTTP request object
    
    Returns:
        Client IP address or None
    """
    # Check X-Forwarded-For header (proxies)
    if "X-Forwarded-For" in request.headers:
        ips = request.headers["X-Forwarded-For"].split(",")
        return ips[0].strip()
    
    # Check X-Real-IP header (nginx)
    if "X-Real-IP" in request.headers:
        return request.headers["X-Real-IP"]
    
    # Direct connection
    return request.client.host if request.client else None

def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolve hostname to IP address via DNS lookup.
    
    Args:
        hostname: Hostname to resolve
    
    Returns:
        IP address or None if resolution fails
    """
    import socket
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        logger.warning(f"Failed to resolve hostname: {hostname}")
        return None

def is_localhost(ip_string: str) -> bool:
    """
    Check if IP is localhost/loopback address.
    
    Args:
        ip_string: IP address to check
    
    Returns:
        True if localhost, False otherwise
    """
    try:
        ip = ipaddress.ip_address(ip_string)
        return ip.is_loopback
    except ValueError:
        return False
```

**Features**:
- IPv4/IPv6 validation
- Private/public IP detection
- Client IP extraction from requests
- Hostname resolution
- Localhost detection

**Usage**:
```python
from app.utils.ip_utils import (
    validate_ip_address,
    is_private_ip,
    get_client_ip_address,
    resolve_hostname
)

# Validate IP
if validate_ip_address("192.168.1.1"):
    print("Valid IP")

# Check if private
if is_private_ip("10.0.0.1"):
    print("Private IP")

# Get client IP from request
client_ip = get_client_ip_address(request)

# Resolve hostname
ip = resolve_hostname("example.com")
```

### port_utils.py
Port management and validation.

**Planned Functions**:

```python
import socket
from typing import Optional

def validate_port(port: int) -> bool:
    """
    Validate port number is in valid range (0-65535).
    
    Args:
        port: Port number to validate
    
    Returns:
        True if valid, False otherwise
    """
    return 0 < port < 65536

def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """
    Check if port is available for binding.
    
    Args:
        port: Port to check
        host: Host to bind to
    
    Returns:
        True if available, False if in use
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
        return True
    except OSError:
        return False

def is_port_in_use(port: int, host: str = "0.0.0.0") -> bool:
    """
    Check if port is currently in use.
    
    Args:
        port: Port to check
        host: Host to check
    
    Returns:
        True if in use, False if available
    """
    return not is_port_available(port, host)

def get_next_available_port(
    start_port: int = 9221,
    max_port: int = 9999,
    host: str = "0.0.0.0"
) -> Optional[int]:
    """
    Find next available port in range.
    
    Args:
        start_port: Starting port for search
        max_port: Maximum port to check
        host: Host to bind to
    
    Returns:
        Available port number or None if no ports available
    
    Raises:
        ValueError: If port range is invalid
    """
    if start_port >= max_port:
        raise ValueError(f"Invalid port range: {start_port}-{max_port}")
    
    for port in range(start_port, max_port + 1):
        if is_port_available(port, host):
            return port
    
    return None

def get_port_range_status(
    start_port: int = 9221,
    max_port: int = 9999,
    host: str = "0.0.0.0"
) -> dict:
    """
    Get status of all ports in range.
    
    Args:
        start_port: Starting port
        max_port: Ending port
        host: Host to check
    
    Returns:
        Dict with status info
    """
    status = {
        "total": max_port - start_port + 1,
        "available": 0,
        "in_use": 0,
        "ports": {}
    }
    
    for port in range(start_port, max_port + 1):
        if is_port_available(port, host):
            status["available"] += 1
            status["ports"][port] = "available"
        else:
            status["in_use"] += 1
            status["ports"][port] = "in_use"
    
    return status
```

**Features**:
- Port range validation
- Port availability checking
- Finding next available port
- Port status reporting

**Usage**:
```python
from app.utils.port_utils import (
    validate_port,
    is_port_available,
    get_next_available_port,
    get_port_range_status
)

# Validate port
if validate_port(9221):
    print("Valid port")

# Check if available
if is_port_available(9221):
    print("Port is free")

# Find available port
port = get_next_available_port(9221, 9999)
print(f"Use port: {port}")

# Check port range status
status = get_port_range_status(9221, 9230)
print(f"Available: {status['available']}/{status['total']}")
```

## Integration Examples

### Registering a Client

```python
from app.utils.ip_utils import validate_ip_address, resolve_hostname
from app.utils.port_utils import get_next_available_port

def register_client(hostname: str, ip_address: str):
    # Validate IP
    if not validate_ip_address(ip_address):
        raise ValidationError("Invalid IP address", field="ip_address")
    
    # Try to resolve
    resolved_ip = resolve_hostname(hostname)
    
    # Assign port
    assigned_port = get_next_available_port()
    if assigned_port is None:
        raise resourceError("No available ports")
    
    # Create client
    client = create_client(hostname, ip_address, assigned_port)
    return client
```

### Health Check

```python
from app.utils.port_utils import get_port_range_status

def check_port_availability():
    status = get_port_range_status(9221, 9999)
    
    if status["available"] < 10:
        logger.warning(f"Low available ports: {status['available']}")
    
    return status
```

## Best Practices

1. **Validate early**: Check IP/port formats immediately
2. **Handle errors**: Use appropriate exceptions
3. **Cache results**: Cache DNS resolutions
4. **Rate limiting**: Don't check ports too frequently
5. **Logging**: Log port allocation for debugging
6. **Testing**: Test edge cases (min/max ports)

## Testing

```python
import pytest
from app.utils.ip_utils import validate_ip_address
from app.utils.port_utils import validate_port, get_next_available_port

def test_validate_ip():
    assert validate_ip_address("192.168.1.1")
    assert validate_ip_address("2001:db8::1")
    assert not validate_ip_address("999.999.999.999")

def test_validate_port():
    assert validate_port(8000)
    assert validate_port(9999)
    assert not validate_port(0)
    assert not validate_port(99999)

def test_get_next_available_port():
    port = get_next_available_port(9221, 9999)
    assert port is not None
    assert 9221 <= port <= 9999
```

## Status: Phase 4 Implementation

This module will be implemented in Phase 4 (Utility Functions) as per the implementation plan.

## See Also

- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md#phase-4-utility-functions-week-3)
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md) - Quick reference
