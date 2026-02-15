"""
PyArgus API Unit Tests.

Test cases for all API endpoints using pytest and the request builder module.
Tests include success cases, error cases, and edge cases.

Usage:
    pytest test_api_endpoints.py -v
"""

import pytest
import time
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api_request_builder import (
    send_request,
    validate_status_code,
    extract_client_id,
    extract_assigned_port,
    APIRequestError,
    # Request builders
    build_register_request,
    build_register_request_empty_fields,
    build_register_request_missing_hostname,
    build_auth_request,
    build_auth_request_old_timestamp,
    build_auth_request_empty_signature,
    build_auth_request_missing_fields,
    build_service_pre_config_request,
    build_service_install_request,
    build_service_install_request_empty_client,
    build_service_status_request,
    build_health_check_request,
    build_list_clients_request,
    build_get_client_request,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def api_base_url():
    """Get base API URL."""
    return "http://localhost:5000/api"


@pytest.fixture(scope="session")
def registered_client(api_base_url):
    """Register a test client and return its details."""
    request = build_register_request(
        hostname="pytest-client.local",
        ip_address="192.168.1.200",
        public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB... pytest@test"
    )
    
    try:
        status_code, response = send_request(request, api_base_url)
        if status_code == 201:
            return {
                'client_id': response.get('client_id'),
                'assigned_port': response.get('assigned_port'),
                'hostname': 'pytest-client.local',
                'public_key': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB... pytest@test'
            }
    except APIRequestError:
        pass
    
    # Return None if registration fails (test will skip)
    return None


# ============================================================================
# Tests: Client Registration Endpoint
# ============================================================================

class TestClientRegistration:
    """Tests for client registration endpoint."""
    
    def test_register_client_success(self, api_base_url):
        """Test successful client registration."""
        request = build_register_request(
            hostname="test-success.local",
            ip_address="192.168.1.101",
            public_key="ssh-rsa AAAAB3Nza... test@success"
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert validate_status_code(status_code, 201), f"Expected 201, got {status_code}"
        assert response['status'] == 'success'
        assert 'client_id' in response
        assert 'assigned_port' in response
        assert isinstance(response['assigned_port'], int)
        assert 9221 <= response['assigned_port'] <= 9999
    
    def test_register_client_empty_hostname(self, api_base_url):
        """Test registration with empty hostname."""
        request = build_register_request_empty_fields(
            hostname="",
            ip_address="192.168.1.102",
            public_key="ssh-rsa AAAA... test@empty"
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 400
        assert response['status'] == 'error'
        assert 'error_code' in response
    
    def test_register_client_empty_ip_address(self, api_base_url):
        """Test registration with empty IP address."""
        request = build_register_request_empty_fields(
            hostname="test-empty-ip.local",
            ip_address="",
            public_key="ssh-rsa AAAA... test@empty"
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 400
        assert response['status'] == 'error'
    
    def test_register_client_empty_public_key(self, api_base_url):
        """Test registration with empty public key."""
        request = build_register_request_empty_fields(
            hostname="test-empty-key.local",
            ip_address="192.168.1.103",
            public_key=""
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 400
        assert response['status'] == 'error'
    
    def test_register_client_missing_hostname(self, api_base_url):
        """Test registration with missing hostname."""
        request = build_register_request_missing_hostname(
            ip_address="192.168.1.104",
            public_key="ssh-rsa AAAA... test@missing"
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 400
        assert response['status'] == 'error'
        assert 'error_code' in response
    
    def test_register_client_duplicate_key(self, api_base_url, registered_client):
        """Test registering duplicate public key."""
        if not registered_client:
            pytest.skip("No registered client available")
        
        request = build_register_request(
            hostname="test-duplicate.local",
            ip_address="192.168.1.150",
            public_key=registered_client['public_key']  # Duplicate
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 409
        assert response['status'] == 'error'
        assert response['error_code'] == 'DUPLICATE_CLIENT'


# ============================================================================
# Tests: Authentication Endpoint
# ============================================================================

class TestAuthentication:
    """Tests for authentication endpoint."""
    
    def test_auth_success(self, api_base_url, registered_client):
        """Test successful authentication."""
        if not registered_client:
            pytest.skip("No registered client available")
        
        request = build_auth_request(
            client_id=registered_client['client_id'],
            signature="valid_signature_" + str(int(time.time())),
            timestamp=int(time.time())
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 200
        assert response['status'] == 'success'
        assert response.get('authenticated') is True
    
    def test_auth_invalid_client(self, api_base_url):
        """Test authentication with invalid client."""
        request = build_auth_request(
            client_id="non-existent-client-id",
            signature="some_signature",
            timestamp=int(time.time())
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 404
        assert response['status'] == 'error'
        assert response['error_code'] == 'CLIENT_NOT_FOUND'
    
    def test_auth_empty_signature(self, api_base_url, registered_client):
        """Test authentication with empty signature."""
        if not registered_client:
            pytest.skip("No registered client available")
        
        request = build_auth_request_empty_signature(
            client_id=registered_client['client_id']
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 401
        assert response['status'] == 'error'
    
    def test_auth_old_timestamp(self, api_base_url, registered_client):
        """Test authentication with old timestamp."""
        if not registered_client:
            pytest.skip("No registered client available")
        
        request = build_auth_request_old_timestamp(
            client_id=registered_client['client_id'],
            signature="valid_signature",
            seconds_old=600  # 10 minutes old
        )
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 401
        assert response['status'] == 'error'
        assert response['error_code'] == 'INVALID_TIMESTAMP'
    
    def test_auth_missing_fields(self, api_base_url):
        """Test authentication with missing fields."""
        request = build_auth_request_missing_fields()
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 400
        assert response['status'] == 'error'


# ============================================================================
# Tests: Service Pre-Configuration Endpoint
# ============================================================================

class TestServicePreConfig:
    """Tests for service pre-configuration endpoint."""
    
    def test_service_pre_config_success(self, api_base_url, registered_client):
        """Test successful service pre-configuration."""
        if not registered_client:
            pytest.skip("No registered client available")
        
        request = build_service_pre_config_request(registered_client['client_id'])
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 200
        assert response['status'] == 'success'
        assert response['client_id'] == registered_client['client_id']
        assert 'assigned_port' in response
        assert 'hostname' in response
        assert 'ip_address' in response
    
    def test_service_pre_config_invalid_client(self, api_base_url):
        """Test pre-config with invalid client."""
        request = build_service_pre_config_request("non-existent-client-id")
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 404
        assert response['status'] == 'error'
        assert response['error_code'] == 'CLIENT_NOT_FOUND'


# ============================================================================
# Tests: Service Installation Endpoint
# ============================================================================

class TestServiceInstallation:
    """Tests for service installation endpoint."""
    
    def test_service_install_success(self, api_base_url, registered_client):
        """Test successful service file generation."""
        if not registered_client:
            pytest.skip("No registered client available")
        
        request = build_service_install_request(registered_client['client_id'])
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 200
        assert response['status'] == 'success'
        assert 'service_file_content' in response
        assert 'assigned_port' in response
        assert isinstance(response['service_file_content'], str)
        assert '[Unit]' in response['service_file_content']
        assert '[Service]' in response['service_file_content']
        assert '[Install]' in response['service_file_content']
    
    def test_service_install_invalid_client(self, api_base_url):
        """Test install for invalid client."""
        request = build_service_install_request("non-existent-client-id")
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 404
        assert response['status'] == 'error'
    
    def test_service_install_empty_client_id(self, api_base_url):
        """Test install with empty client ID."""
        request = build_service_install_request_empty_client()
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 400
        assert response['status'] == 'error'


# ============================================================================
# Tests: Service Status Endpoint
# ============================================================================

class TestServiceStatus:
    """Tests for service status endpoint."""
    
    def test_service_status_success(self, api_base_url, registered_client):
        """Test successful status check."""
        if not registered_client:
            pytest.skip("No registered client available")
        
        request = build_service_status_request(registered_client['client_id'])
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 200
        assert 'status' in response
        assert response['client_id'] == registered_client['client_id']
        assert 'tunnel_active' in response
    
    def test_service_status_invalid_client(self, api_base_url):
        """Test status check for invalid client."""
        request = build_service_status_request("non-existent-client-id")
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 404
        assert response['status'] == 'error'


# ============================================================================
# Tests: Health Check Endpoint
# ============================================================================

class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_check(self, api_base_url):
        """Test health check endpoint."""
        request = build_health_check_request()
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 200
        assert response['status'] == 'healthy'
        assert 'version' in response
        assert 'services' in response
    
    def test_health_check_services_structure(self, api_base_url):
        """Test health check services structure."""
        request = build_health_check_request()
        
        status_code, response = send_request(request, api_base_url)
        
        services = response.get('services', {})
        assert 'database' in services
        assert 'ssh_manager' in services
        assert 'security' in services


# ============================================================================
# Tests: List Clients Endpoint
# ============================================================================

class TestListClients:
    """Tests for list clients endpoint."""
    
    def test_list_clients(self, api_base_url):
        """Test listing all clients."""
        request = build_list_clients_request()
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 200
        assert response['status'] == 'success'
        assert 'clients' in response
        assert isinstance(response['clients'], list)
        assert 'total' in response
    
    def test_list_clients_structure(self, api_base_url):
        """Test structure of client list response."""
        request = build_list_clients_request()
        
        status_code, response = send_request(request, api_base_url)
        
        if response['total'] > 0:
            client = response['clients'][0]
            assert 'client_id' in client
            assert 'hostname' in client
            assert 'ip_address' in client
            assert 'assigned_port' in client


# ============================================================================
# Tests: Get Client Details Endpoint
# ============================================================================

class TestGetClient:
    """Tests for get client details endpoint."""
    
    def test_get_client_success(self, api_base_url, registered_client):
        """Test getting client details."""
        if not registered_client:
            pytest.skip("No registered client available")
        
        request = build_get_client_request(registered_client['client_id'])
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 200
        assert response['status'] == 'success'
        assert 'client' in response
        assert response['client']['client_id'] == registered_client['client_id']
    
    def test_get_client_invalid(self, api_base_url):
        """Test getting invalid client."""
        request = build_get_client_request("non-existent-client-id")
        
        status_code, response = send_request(request, api_base_url)
        
        assert status_code == 404
        assert response['status'] == 'error'
        assert response['error_code'] == 'CLIENT_NOT_FOUND'


# ============================================================================
# Connection Tests
# ============================================================================

class TestAPIConnection:
    """Tests for API connection."""
    
    def test_api_connection(self, api_base_url):
        """Test that API is accessible."""
        request = build_health_check_request()
        
        try:
            status_code, response = send_request(request, api_base_url)
            assert status_code in [200, 500]  # Accept 200 or 500, just need to connect
        except APIRequestError as e:
            pytest.fail(f"API connection failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
