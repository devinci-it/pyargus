"""
PyArgus API Testing & Demo Guide

This document explains how to use the API demo and testing tools.
"""

# PyArgus API Testing & Demo Guide

## Overview

PyArgus includes three tools for testing and demonstrating the API:

1. **api_demo.py** - Interactive demo showing all API endpoints with success and error cases
2. **api_request_builder.py** - Reusable request construction functions for programmatic API testing
3. **test_api_endpoints.py** - Comprehensive pytest test suite for all endpoints

## Prerequisites

### 1. Start the PyArgus API Server

The API must be running before executing any tests or demos.

```bash
# From the project root
python -m pyargus.app
# or
python scripts/start_server.py
```

The server should be accessible at: `http://localhost:5000`

### 2. Install Test Dependencies

```bash
# For demo and request builder
pip install requests

# For pytest test suite
pip install pytest requests
```

## 1. API Demo (api_demo.py)

### Purpose
Interactive demonstration of all API endpoints, including success cases and error/edge cases.

### Usage

```bash
# Navigate to scripts directory
cd scripts

# Run the complete demo
python api_demo.py
```

### What It Tests

#### Section 1: Client Registration (6 tests)
- ✅ Successful registration
- ❌ Missing required fields
- ❌ Invalid JSON format
- ❌ Empty string fields
- ❌ Duplicate public key registration
- ❌ Wrong Content-Type header

#### Section 2: Authentication (6 tests)
- ✅ Successful authentication
- ❌ Invalid/non-existent client
- ❌ Empty signature
- ❌ Timestamp too old (>5 minutes)
- ❌ Missing required fields
- ❌ Invalid timestamp type

#### Section 3: Service Pre-Configuration (3 tests)
- ✅ Successful pre-configuration
- ❌ Invalid client ID
- ❌ Empty client ID

#### Section 4: Service Installation (4 tests)
- ✅ Successful service file generation
- ❌ Invalid client ID
- ❌ Missing client_id field
- ❌ Empty client_id value

#### Section 5: Service Status (2 tests)
- ✅ Successful status check
- ❌ Invalid client ID

#### Section 6: Health Check (1 test)
- ✅ Health check status

#### Section 7: List Clients (1 test)
- ✅ List all registered clients

#### Section 8: Get Client Details (2 tests)
- ✅ Get details for valid client
- ❌ Get details for invalid client

### Output Format

```
================================================================================
  1.1 - Register Client (Success Case)
================================================================================

[REQUEST] POST /api/register
[BODY] {
  "hostname": "client-01.example.com",
  "ip_address": "192.168.1.100",
  "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7vb... user@client-01"
}

[RESPONSE] Status Code: 201
[BODY] {
  "status": "success",
  "client_id": "uuid-string",
  "assigned_port": 9221,
  "message": "Client registered successfully"
}

[INFO] Client stored for subsequent tests
```

## 2. API Request Builder (api_request_builder.py)

### Purpose
Reusable Python functions for constructing and sending API requests. Useful for:
- Integration tests
- Client code development
- Automation scripts

### Usage

#### As a Module

```python
from api_request_builder import (
    send_request,
    build_register_request,
    build_auth_request,
    build_health_check_request,
)

# Build a registration request
request = build_register_request(
    hostname="client.example.com",
    ip_address="192.168.1.100",
    public_key="ssh-rsa AAAA... user@client"
)

# Send the request
status_code, response = send_request(request)

# Use response
if status_code == 201:
    client_id = response['client_id']
    assigned_port = response['assigned_port']
```

#### As a Script

```bash
python api_request_builder.py
```

This runs an example that demonstrates basic functionality.

### Available Request Builders

#### Registration Requests
```python
build_register_request(hostname, ip_address, public_key)
build_register_request_missing_hostname(ip_address, public_key)
build_register_request_empty_fields(hostname="", ip_address="", public_key="")
build_register_request_invalid_types()
```

#### Authentication Requests
```python
build_auth_request(client_id, signature, timestamp=None)
build_auth_request_old_timestamp(client_id, signature, seconds_old=600)
build_auth_request_future_timestamp(client_id, signature, seconds_future=600)
build_auth_request_empty_signature(client_id, timestamp=None)
build_auth_request_missing_fields()
build_auth_request_invalid_timestamp_type(client_id, signature)
```

#### Service Requests
```python
build_service_pre_config_request(client_id)
build_service_install_request(client_id)
build_service_status_request(client_id)
```

#### Other Requests
```python
build_health_check_request()
build_list_clients_request(limit=None, offset=None)
build_get_client_request(client_id)
```

### Helper Functions

```python
# Send a request
status_code, response = send_request(request, base_url=None, timeout=None)

# Extract data from response
client_id = extract_client_id(response)
assigned_port = extract_assigned_port(response)

# Validate status codes
if validate_status_code(status_code, 201):
    print("Success!")
```

### Test Scenarios

The module includes scenario builders for complex test flows:

```python
from api_request_builder import (
    APITestScenario,
    scenario_full_registration_flow,
    scenario_error_handling,
)

# Use predefined scenarios
scenario = scenario_error_handling()
results = scenario.execute("http://localhost:5000/api")
print(scenario.summary())

# Or create custom scenarios
scenario = APITestScenario(
    "My Test",
    "Testing my custom flow"
)

scenario.add_step(
    build_register_request(...),
    expected_status=201,
    expected_fields=['client_id', 'assigned_port']
)

scenario.add_step(
    build_auth_request(...),
    expected_status=200,
)

results = scenario.execute()
```

## 3. Pytest Test Suite (test_api_endpoints.py)

### Purpose
Comprehensive automated test suite using pytest framework.

### Usage

```bash
# Navigate to tests directory or run from project root

# Run all tests
pytest tests/test_api_endpoints.py -v

# Run specific test class
pytest tests/test_api_endpoints.py::TestClientRegistration -v

# Run specific test
pytest tests/test_api_endpoints.py::TestClientRegistration::test_register_client_success -v

# Run with coverage
pytest tests/test_api_endpoints.py --cov=pyargus.api --cov-report=html

# Run with detailed output
pytest tests/test_api_endpoints.py -vv --tb=long
```

### Test Organization

#### Test Classes
- `TestClientRegistration` - 6 registration tests
- `TestAuthentication` - 5 authentication tests
- `TestServicePreConfig` - 2 pre-configuration tests
- `TestServiceInstallation` - 3 installation tests
- `TestServiceStatus` - 2 status tests
- `TestHealthCheck` - 2 health check tests
- `TestListClients` - 2 list clients tests
- `TestGetClient` - 2 get client tests
- `TestAPIConnection` - Connection test

### Fixtures

```python
@pytest.fixture(scope="session")
def api_base_url():
    """Provides base API URL"""
    return "http://localhost:5000/api"

@pytest.fixture(scope="session")
def registered_client(api_base_url):
    """Registers a test client for use in other tests"""
    # Returns client data dict with client_id, assigned_port, etc.
```

### Example Test

```python
def test_register_client_success(self, api_base_url):
    """Test successful client registration."""
    request = build_register_request(
        hostname="test-success.local",
        ip_address="192.168.1.101",
        public_key="ssh-rsa AAAAB3Nza... test@success"
    )
    
    status_code, response = send_request(request, api_base_url)
    
    assert validate_status_code(status_code, 201)
    assert response['status'] == 'success'
    assert 'client_id' in response
```

### Expected Results

When all tests pass, pytest output should look like:

```
tests/test_api_endpoints.py::TestClientRegistration::test_register_client_success PASSED
tests/test_api_endpoints.py::TestClientRegistration::test_register_client_empty_hostname PASSED
...

========================== 20 passed in 2.34s ==========================
```

## Troubleshooting

### "Connection refused" Error

```
APIRequestError: Connection error: [Errno 111] Connection refused
```

**Solution:** Start the API server
```bash
python -m pyargus.app
```

### "Invalid JSON response"

**Solution:** Check that:
1. API server is running
2. API is returning valid JSON
3. Check error logs on the server

### Tests Hanging

**Solution:** Set a shorter timeout or increase timeout value:
```python
send_request(request, timeout=2)  # 2 seconds instead of 5
```

### Some Tests Skipped

If you see `SKIPPED` in pytest output, it means `registered_client` fixture failed.

**Solution:** 
1. Ensure API is running
2. Check registration endpoint is working: visit `/api/health`

## Configuration

### Change Base URL

#### In api_demo.py
```python
BASE_URL = "http://your-api.com/api"
```

#### In api_request_builder.py
```python
API_CONFIG = {
    'base_url': 'http://your-api.com/api',
    'timeout': 5,
    'verify_ssl': True  # For HTTPS
}
```

#### For pytest
```bash
# Modify fixture in test file or pass via conftest.py
pytest tests/test_api_endpoints.py -v
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install flask requests pytest paramiko pycryptodome python-dotenv
      
      - name: Start API server
        run: python -m pyargus.app &
        
      - name: Wait for API
        run: sleep 2
      
      - name: Run pytest
        run: pytest tests/test_api_endpoints.py -v
```

## Error Codes Reference

### Registration Errors
- `400` - Invalid request (missing/empty fields)
- `409` - Duplicate client (public key already registered)
- `500` - Server error

### Authentication Errors
- `400` - Invalid request (missing fields)
- `401` - Invalid signature or old timestamp
- `404` - Client not found
- `500` - Server error

### Service Errors
- `400` - Invalid request (missing/empty client_id)
- `404` - Client not found
- `500` - Server error

### General Errors
- `200` - Success (GET requests)
- `201` - Created (POST registration)
- `400` - Bad request
- `404` - Not found
- `500` - Internal server error

## Best Practices

1. **Always start with demo.py** to understand the API
2. **Use request_builder.py** for custom integrations
3. **Run pytest** before committing code
4. **Check health endpoint** first if debugging
5. **Pipe demo output** to file: `python api_demo.py > test_results.log`

## Next Steps

After successfully running demos and tests:

1. Integrate request builders into your client code
2. Add custom tests for your use cases
3. Set up CI/CD pipeline for automated testing
4. Monitor API performance with test metrics
5. Implement additional error scenarios as needed

