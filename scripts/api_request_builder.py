"""
PyArgus API Request Builders - Reusable functions for constructing API requests.

This module provides individual functions for building and sending requests to
each PyArgus API endpoint. Useful for integration tests and client code.

Usage:
    from api_request_builder import build_register_request, send_request
    
    request = build_register_request(
        hostname="client.example.com",
        ip_address="192.168.1.100",
        public_key="ssh-rsa AAAA..."
    )
    response = send_request(request)
"""

import requests
import json
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

# ============================================================================
# Configuration
# ============================================================================

API_CONFIG = {
    'base_url': 'http://localhost:5000/api',
    'timeout': 5,
    'verify_ssl': False
}


@dataclass
class APIRequest:
    """Represents an API request."""
    method: str
    endpoint: str
    data: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    
    def url(self, base_url: str = None) -> str:
        """Get full URL for request."""
        base = base_url or API_CONFIG['base_url']
        return f"{base}{self.endpoint}"
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.method} {self.endpoint}"


class APIRequestError(Exception):
    """Exception raised for API request errors."""
    pass


# ============================================================================
# Helper Functions
# ============================================================================

def send_request(
    request: APIRequest,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None
) -> Tuple[int, Dict[str, Any]]:
    """
    Send an API request and return status code and response data.
    
    Args:
        request: APIRequest instance
        base_url: Optional override for base URL
        timeout: Optional override for timeout
        
    Returns:
        Tuple of (status_code, response_data)
        
    Raises:
        APIRequestError: If request fails
    """
    try:
        url = request.url(base_url or API_CONFIG['base_url'])
        timeout_val = timeout or API_CONFIG['timeout']
        headers = request.headers or {'Content-Type': 'application/json'}
        
        if request.method == 'GET':
            response = requests.get(
                url,
                params=request.params,
                headers=headers,
                timeout=timeout_val,
                verify=API_CONFIG['verify_ssl']
            )
        elif request.method == 'POST':
            response = requests.post(
                url,
                json=request.data,
                headers=headers,
                timeout=timeout_val,
                verify=API_CONFIG['verify_ssl']
            )
        elif request.method == 'DELETE':
            response = requests.delete(
                url,
                headers=headers,
                timeout=timeout_val,
                verify=API_CONFIG['verify_ssl']
            )
        else:
            raise APIRequestError(f"Unsupported HTTP method: {request.method}")
        
        response_data = response.json() if response.text else {}
        return response.status_code, response_data
        
    except requests.exceptions.ConnectionError as e:
        raise APIRequestError(f"Connection error: {str(e)}")
    except requests.exceptions.Timeout as e:
        raise APIRequestError(f"Request timeout: {str(e)}")
    except json.JSONDecodeError as e:
        raise APIRequestError(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise APIRequestError(f"Request failed: {str(e)}")


def validate_status_code(status_code: int, expected: int) -> bool:
    """
    Validate that status code matches expected value.
    
    Args:
        status_code: Actual status code
        expected: Expected status code
        
    Returns:
        True if matches, False otherwise
    """
    return status_code == expected


def extract_client_id(response: Dict[str, Any]) -> Optional[str]:
    """Extract client_id from response."""
    return response.get('client_id')


def extract_assigned_port(response: Dict[str, Any]) -> Optional[int]:
    """Extract assigned_port from response."""
    return response.get('assigned_port')


# ============================================================================
# 1. CLIENT REGISTRATION REQUEST BUILDERS
# ============================================================================

def build_register_request(
    hostname: str,
    ip_address: str,
    public_key: str
) -> APIRequest:
    """
    Build a client registration request.
    
    Args:
        hostname: Client hostname
        ip_address: Client IP address
        public_key: Client public SSH key
        
    Returns:
        APIRequest instance
    """
    return APIRequest(
        method='POST',
        endpoint='/register',
        data={
            'hostname': hostname,
            'ip_address': ip_address,
            'public_key': public_key
        }
    )


def build_register_request_missing_hostname(
    ip_address: str,
    public_key: str
) -> APIRequest:
    """Build registration request with missing hostname (error case)."""
    return APIRequest(
        method='POST',
        endpoint='/register',
        data={
            'ip_address': ip_address,
            'public_key': public_key
        }
    )


def build_register_request_empty_fields(
    hostname: str = "",
    ip_address: str = "",
    public_key: str = ""
) -> APIRequest:
    """Build registration request with empty fields (error case)."""
    return APIRequest(
        method='POST',
        endpoint='/register',
        data={
            'hostname': hostname,
            'ip_address': ip_address,
            'public_key': public_key
        }
    )


def build_register_request_invalid_types() -> APIRequest:
    """Build registration request with invalid field types (error case)."""
    return APIRequest(
        method='POST',
        endpoint='/register',
        data={
            'hostname': 12345,  # Should be string
            'ip_address': ['192.168.1.1'],  # Should be string
            'public_key': {'key': 'value'}  # Should be string
        }
    )


# ============================================================================
# 2. AUTHENTICATION REQUEST BUILDERS
# ============================================================================

def build_auth_request(
    client_id: str,
    signature: str,
    timestamp: Optional[int] = None
) -> APIRequest:
    """
    Build a client authentication request.
    
    Args:
        client_id: Client ID
        signature: Signature (typically signed timestamp)
        timestamp: Unix timestamp (defaults to now)
        
    Returns:
        APIRequest instance
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    return APIRequest(
        method='POST',
        endpoint='/auth',
        data={
            'client_id': client_id,
            'signature': signature,
            'timestamp': timestamp
        }
    )


def build_auth_request_old_timestamp(
    client_id: str,
    signature: str,
    seconds_old: int = 600
) -> APIRequest:
    """Build auth request with old timestamp (error case)."""
    old_timestamp = int(time.time()) - seconds_old
    return build_auth_request(client_id, signature, old_timestamp)


def build_auth_request_future_timestamp(
    client_id: str,
    signature: str,
    seconds_future: int = 600
) -> APIRequest:
    """Build auth request with future timestamp (error case)."""
    future_timestamp = int(time.time()) + seconds_future
    return build_auth_request(client_id, signature, future_timestamp)


def build_auth_request_empty_signature(
    client_id: str,
    timestamp: Optional[int] = None
) -> APIRequest:
    """Build auth request with empty signature (error case)."""
    return build_auth_request(client_id, "", timestamp)


def build_auth_request_missing_fields() -> APIRequest:
    """Build auth request with missing fields (error case)."""
    return APIRequest(
        method='POST',
        endpoint='/auth',
        data={'client_id': 'some-client'}  # Missing signature and timestamp
    )


def build_auth_request_invalid_timestamp_type(
    client_id: str,
    signature: str
) -> APIRequest:
    """Build auth request with invalid timestamp type (error case)."""
    return APIRequest(
        method='POST',
        endpoint='/auth',
        data={
            'client_id': client_id,
            'signature': signature,
            'timestamp': "not_a_number"  # Invalid type
        }
    )


# ============================================================================
# 3. SERVICE PRE-CONFIGURATION REQUEST BUILDERS
# ============================================================================

def build_service_pre_config_request(client_id: str) -> APIRequest:
    """
    Build a service pre-configuration request.
    
    Args:
        client_id: Client ID
        
    Returns:
        APIRequest instance
    """
    return APIRequest(
        method='GET',
        endpoint=f'/service/pre/{client_id}'
    )


def build_service_pre_config_request_empty_client() -> APIRequest:
    """Build pre-config request with empty client ID (error case)."""
    return APIRequest(
        method='GET',
        endpoint='/service/pre/'
    )


# ============================================================================
# 4. SERVICE INSTALLATION REQUEST BUILDERS
# ============================================================================

def build_service_install_request(client_id: str) -> APIRequest:
    """
    Build a service installation request.
    
    Args:
        client_id: Client ID
        
    Returns:
        APIRequest instance
    """
    return APIRequest(
        method='POST',
        endpoint='/service/install',
        data={'client_id': client_id}
    )


def build_service_install_request_empty_client() -> APIRequest:
    """Build install request with empty client ID (error case)."""
    return APIRequest(
        method='POST',
        endpoint='/service/install',
        data={'client_id': ''}
    )


def build_service_install_request_missing_client() -> APIRequest:
    """Build install request with missing client ID (error case)."""
    return APIRequest(
        method='POST',
        endpoint='/service/install',
        data={}
    )


# ============================================================================
# 5. SERVICE STATUS REQUEST BUILDERS
# ============================================================================

def build_service_status_request(client_id: str) -> APIRequest:
    """
    Build a service status request.
    
    Args:
        client_id: Client ID
        
    Returns:
        APIRequest instance
    """
    return APIRequest(
        method='GET',
        endpoint=f'/service/status/{client_id}'
    )


# ============================================================================
# 6. HEALTH CHECK REQUEST BUILDERS
# ============================================================================

def build_health_check_request() -> APIRequest:
    """
    Build a health check request.
    
    Returns:
        APIRequest instance
    """
    return APIRequest(
        method='GET',
        endpoint='/health'
    )


# ============================================================================
# 7. LIST CLIENTS REQUEST BUILDERS
# ============================================================================

def build_list_clients_request(limit: Optional[int] = None, offset: Optional[int] = None) -> APIRequest:
    """
    Build a list clients request.
    
    Args:
        limit: Maximum number of clients to return
        offset: Number of clients to skip
        
    Returns:
        APIRequest instance
    """
    params = {}
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    
    return APIRequest(
        method='GET',
        endpoint='/clients',
        params=params if params else None
    )


# ============================================================================
# 8. GET CLIENT DETAILS REQUEST BUILDERS
# ============================================================================

def build_get_client_request(client_id: str) -> APIRequest:
    """
    Build a get client details request.
    
    Args:
        client_id: Client ID
        
    Returns:
        APIRequest instance
    """
    return APIRequest(
        method='GET',
        endpoint=f'/clients/{client_id}'
    )


# ============================================================================
# Integration Test Scenarios
# ============================================================================

class APITestScenario:
    """Represents an API test scenario with setup, execution, and validation."""
    
    def __init__(self, name: str, description: str):
        """Initialize test scenario."""
        self.name = name
        self.description = description
        self.steps = []
        self.results = []
    
    def add_step(
        self,
        request: APIRequest,
        expected_status: int,
        expected_fields: Optional[list] = None,
        error_expected: bool = False
    ) -> None:
        """Add a test step."""
        self.steps.append({
            'request': request,
            'expected_status': expected_status,
            'expected_fields': expected_fields or [],
            'error_expected': error_expected
        })
    
    def execute(self, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Execute all steps and return results."""
        self.results = []
        
        for i, step in enumerate(self.steps, 1):
            try:
                status_code, response_data = send_request(step['request'], base_url)
                
                result = {
                    'step': i,
                    'request': str(step['request']),
                    'status_code': status_code,
                    'passed': status_code == step['expected_status'],
                    'response': response_data,
                    'error': None
                }
                
                # Check for expected fields
                if step['expected_fields']:
                    missing = [f for f in step['expected_fields'] if f not in response_data]
                    result['missing_fields'] = missing
                    result['passed'] = result['passed'] and len(missing) == 0
                
                self.results.append(result)
                
            except APIRequestError as e:
                self.results.append({
                    'step': i,
                    'request': str(step['request']),
                    'passed': False,
                    'error': str(e)
                })
        
        return {
            'scenario': self.name,
            'description': self.description,
            'total_steps': len(self.steps),
            'passed_steps': sum(1 for r in self.results if r.get('passed', False)),
            'results': self.results
        }
    
    def summary(self) -> str:
        """Get test summary."""
        passed = sum(1 for r in self.results if r.get('passed', False))
        total = len(self.results)
        return f"{self.name}: {passed}/{total} steps passed"


# ============================================================================
# Example Scenarios
# ============================================================================

def scenario_full_registration_flow() -> APITestScenario:
    """Create a full registration and verification flow scenario."""
    scenario = APITestScenario(
        "Full Registration Flow",
        "Register a client, authenticate, get status, and generate service file"
    )
    
    # Step 1: Register client
    scenario.add_step(
        build_register_request(
            hostname="test-client.local",
            ip_address="192.168.1.50",
            public_key="ssh-rsa AAAAB3Nza... test"
        ),
        expected_status=201,
        expected_fields=['client_id', 'assigned_port']
    )
    
    # Note: In real scenario, would extract client_id from first response
    # For demo, using placeholder
    client_id = "will-be-filled-from-response"
    
    return scenario


def scenario_error_handling() -> APITestScenario:
    """Create an error handling scenario."""
    scenario = APITestScenario(
        "Error Handling",
        "Test various error conditions"
    )
    
    # Test 1: Invalid registration
    scenario.add_step(
        build_register_request_empty_fields(),
        expected_status=400,
        error_expected=True
    )
    
    # Test 2: Auth with missing fields
    scenario.add_step(
        build_auth_request_missing_fields(),
        expected_status=400,
        error_expected=True
    )
    
    # Test 3: Invalid client on status check
    scenario.add_step(
        build_service_status_request("non-existent-id"),
        expected_status=404,
        error_expected=True
    )
    
    return scenario


if __name__ == "__main__":
    # Example usage
    print("PyArgus API Request Builder Module")
    print("=" * 50)
    print("\nExample: Building and sending a registration request\n")
    
    request = build_register_request(
        hostname="demo-client.local",
        ip_address="192.168.1.100",
        public_key="ssh-rsa AAAA... demo@local"
    )
    
    print(f"Request: {request}")
    print(f"Endpoint: {request.endpoint}")
    print(f"Data: {request.data}\n")
    
    try:
        status_code, response = send_request(request)
        print(f"Status Code: {status_code}")
        print(f"Response: {json.dumps(response, indent=2)}")
    except APIRequestError as e:
        print(f"Error: {e}")
