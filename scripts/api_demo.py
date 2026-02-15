"""
PyArgus API Demo - Request Construction and Testing.

This module demonstrates how to interact with each PyArgus API endpoint,
including success cases, error cases, and edge cases.

Usage:
    python api_demo.py
    
    Or import and use individual functions:
    from api_demo import demo_register_client, demo_authentication, etc.
"""

import json
import requests
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import time

# ============================================================================
# Configuration
# ============================================================================

BASE_URL = "http://localhost:5000/api"
TIMEOUT = 5  # seconds

# Test data
TEST_CLIENTS = []


# ============================================================================
# Helper Functions
# ============================================================================

def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_request(method: str, endpoint: str, data: Dict = None) -> None:
    """Print request details."""
    print(f"[REQUEST] {method} {endpoint}")
    if data:
        print(f"[BODY] {json.dumps(data, indent=2)}")
    print()


def print_response(status_code: int, response_data: Dict) -> None:
    """Print response details."""
    print(f"[RESPONSE] Status Code: {status_code}")
    print(f"[BODY] {json.dumps(response_data, indent=2)}")
    print()


def handle_request_error(error: Exception) -> None:
    """Handle and print request errors."""
    print(f"[ERROR] {type(error).__name__}: {str(error)}")
    print()


# ============================================================================
# 1. CLIENT REGISTRATION ENDPOINT
# ============================================================================

def demo_register_client_success() -> None:
    """Demo: Successful client registration."""
    print_section("1.1 - Register Client (Success Case)")
    
    endpoint = f"{BASE_URL}/register"
    request_data = {
        "hostname": "client-01.example.com",
        "ip_address": "192.168.1.100",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7vb... user@client-01"
    }
    
    print_request("POST", "/api/register", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
        
        # Store for later use
        if response.status_code == 201:
            TEST_CLIENTS.append({
                'client_id': response_data['client_id'],
                'assigned_port': response_data['assigned_port'],
                'hostname': request_data['hostname'],
                'public_key': request_data['public_key']
            })
            print("[INFO] Client stored for subsequent tests\n")
    except Exception as e:
        handle_request_error(e)


def demo_register_client_missing_fields() -> None:
    """Demo: Registration with missing required fields."""
    print_section("1.2 - Register Client (Missing Fields - Error Case)")
    
    endpoint = f"{BASE_URL}/register"
    request_data = {
        "hostname": "client-02.example.com"
        # Missing: ip_address, public_key
    }
    
    print_request("POST", "/api/register", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_register_client_invalid_json() -> None:
    """Demo: Registration with invalid JSON."""
    print_section("1.3 - Register Client (Invalid JSON - Error Case)")
    
    endpoint = f"{BASE_URL}/register"
    
    print_request("POST", "/api/register", None)
    print("[BODY] Invalid JSON: {hostname: 'client', missing quotes...}\n")
    
    try:
        response = requests.post(
            endpoint,
            data="Invalid JSON",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_register_client_empty_strings() -> None:
    """Demo: Registration with empty string fields."""
    print_section("1.4 - Register Client (Empty Strings - Error Case)")
    
    endpoint = f"{BASE_URL}/register"
    request_data = {
        "hostname": "",  # Empty
        "ip_address": "192.168.1.101",
        "public_key": "ssh-rsa AAAA... user@client"
    }
    
    print_request("POST", "/api/register", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_register_duplicate_key() -> None:
    """Demo: Register client with duplicate public key."""
    print_section("1.5 - Register Client (Duplicate Key - Error Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run success case first.\n")
        return
    
    endpoint = f"{BASE_URL}/register"
    existing_client = TEST_CLIENTS[0]
    
    request_data = {
        "hostname": "client-duplicate.example.com",
        "ip_address": "192.168.1.200",
        "public_key": existing_client['public_key']  # Same key
    }
    
    print_request("POST", "/api/register", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_register_client_wrong_content_type() -> None:
    """Demo: Registration with wrong Content-Type."""
    print_section("1.6 - Register Client (Wrong Content-Type - Error Case)")
    
    endpoint = f"{BASE_URL}/register"
    request_data = {
        "hostname": "client-03.example.com",
        "ip_address": "192.168.1.102",
        "public_key": "ssh-rsa AAAA... user@client"
    }
    
    print_request("POST", "/api/register (Content-Type: text/plain)", request_data)
    
    try:
        response = requests.post(
            endpoint,
            data=json.dumps(request_data),
            headers={"Content-Type": "text/plain"},
            timeout=TIMEOUT
        )
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


# ============================================================================
# 2. AUTHENTICATION ENDPOINT
# ============================================================================

def demo_authentication_success() -> None:
    """Demo: Successful client authentication."""
    print_section("2.1 - Authenticate Client (Success Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run register first.\n")
        return
    
    client = TEST_CLIENTS[0]
    endpoint = f"{BASE_URL}/auth"
    
    # Create valid signature and timestamp
    current_timestamp = int(time.time())
    request_data = {
        "client_id": client['client_id'],
        "signature": "valid_signature_here_" + str(current_timestamp),
        "timestamp": current_timestamp
    }
    
    print_request("POST", "/api/auth", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_authentication_invalid_client() -> None:
    """Demo: Authentication with non-existent client."""
    print_section("2.2 - Authenticate Client (Invalid Client - Error Case)")
    
    endpoint = f"{BASE_URL}/auth"
    request_data = {
        "client_id": "non-existent-client-id-12345",
        "signature": "some_signature",
        "timestamp": int(time.time())
    }
    
    print_request("POST", "/api/auth", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_authentication_empty_signature() -> None:
    """Demo: Authentication with empty signature."""
    print_section("2.3 - Authenticate Client (Empty Signature - Error Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run register first.\n")
        return
    
    client = TEST_CLIENTS[0]
    endpoint = f"{BASE_URL}/auth"
    
    request_data = {
        "client_id": client['client_id'],
        "signature": "",  # Empty signature
        "timestamp": int(time.time())
    }
    
    print_request("POST", "/api/auth", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_authentication_old_timestamp() -> None:
    """Demo: Authentication with too-old timestamp."""
    print_section("2.4 - Authenticate Client (Old Timestamp - Error Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run register first.\n")
        return
    
    client = TEST_CLIENTS[0]
    endpoint = f"{BASE_URL}/auth"
    
    # Timestamp from 10 minutes ago (beyond 5-minute tolerance)
    old_timestamp = int(time.time()) - 600
    request_data = {
        "client_id": client['client_id'],
        "signature": "valid_signature",
        "timestamp": old_timestamp
    }
    
    print_request("POST", "/api/auth", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_authentication_missing_fields() -> None:
    """Demo: Authentication with missing fields."""
    print_section("2.5 - Authenticate Client (Missing Fields - Error Case)")
    
    endpoint = f"{BASE_URL}/auth"
    request_data = {
        "client_id": "some-client-id"
        # Missing: signature, timestamp
    }
    
    print_request("POST", "/api/auth", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_authentication_invalid_timestamp_type() -> None:
    """Demo: Authentication with invalid timestamp type."""
    print_section("2.6 - Authenticate Client (Invalid Timestamp Type - Error Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run register first.\n")
        return
    
    client = TEST_CLIENTS[0]
    endpoint = f"{BASE_URL}/auth"
    
    request_data = {
        "client_id": client['client_id'],
        "signature": "valid_signature",
        "timestamp": "not_an_integer"  # Invalid type
    }
    
    print_request("POST", "/api/auth", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


# ============================================================================
# 3. SERVICE PRE-CONFIGURATION ENDPOINT
# ============================================================================

def demo_service_pre_config_success() -> None:
    """Demo: Successful service pre-configuration."""
    print_section("3.1 - Service Pre-Config (Success Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run register first.\n")
        return
    
    client = TEST_CLIENTS[0]
    endpoint = f"{BASE_URL}/service/pre/{client['client_id']}"
    
    print_request("GET", f"/api/service/pre/{client['client_id']}")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_service_pre_config_invalid_client() -> None:
    """Demo: Pre-config with non-existent client."""
    print_section("3.2 - Service Pre-Config (Invalid Client - Error Case)")
    
    endpoint = f"{BASE_URL}/service/pre/non-existent-client-id"
    
    print_request("GET", "/api/service/pre/non-existent-client-id")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_service_pre_config_empty_client_id() -> None:
    """Demo: Pre-config with empty client ID."""
    print_section("3.3 - Service Pre-Config (Empty Client ID - Error Case)")
    
    endpoint = f"{BASE_URL}/service/pre/  "  # Would be normalized
    
    print_request("GET", "/api/service/pre/ (empty)")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


# ============================================================================
# 4. SERVICE INSTALLATION ENDPOINT
# ============================================================================

def demo_service_install_success() -> None:
    """Demo: Successful service file generation."""
    print_section("4.1 - Service Install (Success Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run register first.\n")
        return
    
    client = TEST_CLIENTS[0]
    endpoint = f"{BASE_URL}/service/install"
    request_data = {
        "client_id": client['client_id']
    }
    
    print_request("POST", "/api/service/install", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        
        # Don't print full service file content, just summary
        if 'service_file_content' in response_data:
            service_content = response_data['service_file_content']
            response_data['service_file_content'] = f"[{len(service_content)} chars - systemd service file]"
        
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_service_install_invalid_client() -> None:
    """Demo: Service install for non-existent client."""
    print_section("4.2 - Service Install (Invalid Client - Error Case)")
    
    endpoint = f"{BASE_URL}/service/install"
    request_data = {
        "client_id": "non-existent-client-id"
    }
    
    print_request("POST", "/api/service/install", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_service_install_missing_client_id() -> None:
    """Demo: Service install with missing client_id."""
    print_section("4.3 - Service Install (Missing Client ID - Error Case)")
    
    endpoint = f"{BASE_URL}/service/install"
    request_data = {}  # Missing client_id
    
    print_request("POST", "/api/service/install", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_service_install_empty_client_id() -> None:
    """Demo: Service install with empty client_id."""
    print_section("4.4 - Service Install (Empty Client ID - Error Case)")
    
    endpoint = f"{BASE_URL}/service/install"
    request_data = {
        "client_id": ""  # Empty
    }
    
    print_request("POST", "/api/service/install", request_data)
    
    try:
        response = requests.post(endpoint, json=request_data, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


# ============================================================================
# 5. SERVICE STATUS ENDPOINT
# ============================================================================

def demo_service_status_success() -> None:
    """Demo: Successful service status check."""
    print_section("5.1 - Service Status (Success Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run register first.\n")
        return
    
    client = TEST_CLIENTS[0]
    endpoint = f"{BASE_URL}/service/status/{client['client_id']}"
    
    print_request("GET", f"/api/service/status/{client['client_id']}")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_service_status_invalid_client() -> None:
    """Demo: Status check for non-existent client."""
    print_section("5.2 - Service Status (Invalid Client - Error Case)")
    
    endpoint = f"{BASE_URL}/service/status/non-existent-client-id"
    
    print_request("GET", "/api/service/status/non-existent-client-id")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


# ============================================================================
# 6. HEALTH CHECK ENDPOINT
# ============================================================================

def demo_health_check() -> None:
    """Demo: Health check endpoint."""
    print_section("6.1 - Health Check")
    
    endpoint = f"{BASE_URL}/health"
    
    print_request("GET", "/api/health")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


# ============================================================================
# 7. LIST CLIENTS ENDPOINT
# ============================================================================

def demo_list_clients() -> None:
    """Demo: List all clients."""
    print_section("7.1 - List Clients")
    
    endpoint = f"{BASE_URL}/clients"
    
    print_request("GET", "/api/clients")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        
        # Truncate client list in output if too large
        if 'clients' in response_data and len(response_data['clients']) > 3:
            original_count = len(response_data['clients'])
            response_data['clients'] = response_data['clients'][:2]
            response_data['_note'] = f"(Showing 2 of {original_count} clients)"
        
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


# ============================================================================
# 8. GET CLIENT DETAILS ENDPOINT
# ============================================================================

def demo_get_client_success() -> None:
    """Demo: Get details for specific client."""
    print_section("8.1 - Get Client Details (Success Case)")
    
    if not TEST_CLIENTS:
        print("[SKIP] No existing clients. Run register first.\n")
        return
    
    client = TEST_CLIENTS[0]
    endpoint = f"{BASE_URL}/clients/{client['client_id']}"
    
    print_request("GET", f"/api/clients/{client['client_id']}")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


def demo_get_client_invalid() -> None:
    """Demo: Get details for non-existent client."""
    print_section("8.2 - Get Client Details (Invalid Client - Error Case)")
    
    endpoint = f"{BASE_URL}/clients/non-existent-client-id"
    
    print_request("GET", "/api/clients/non-existent-client-id")
    
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response_data = response.json()
        print_response(response.status_code, response_data)
    except Exception as e:
        handle_request_error(e)


# ============================================================================
# Main Demo Runner
# ============================================================================

def main():
    """Run all API demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PyArgus API Demo - Request Construction" + " " * 20 + "║")
    print("║" + " " * 10 + "This demo tests all API endpoints with success and error cases" + " " * 8 + "║")
    print("╚" + "=" * 78 + "╝")
    print(f"\n[INFO] Base URL: {BASE_URL}")
    print(f"[INFO] Timeout: {TIMEOUT} seconds")
    print("[INFO] Make sure the PyArgus API server is running on localhost:5000\n")
    
    # ========================================================================
    # Section 1: Client Registration
    # ========================================================================
    print_section("SECTION 1: CLIENT REGISTRATION")
    demo_register_client_success()
    demo_register_client_missing_fields()
    demo_register_client_invalid_json()
    demo_register_client_empty_strings()
    demo_register_duplicate_key()
    demo_register_client_wrong_content_type()
    
    # ========================================================================
    # Section 2: Authentication
    # ========================================================================
    print_section("SECTION 2: AUTHENTICATION")
    demo_authentication_success()
    demo_authentication_invalid_client()
    demo_authentication_empty_signature()
    demo_authentication_old_timestamp()
    demo_authentication_missing_fields()
    demo_authentication_invalid_timestamp_type()
    
    # ========================================================================
    # Section 3: Service Pre-Configuration
    # ========================================================================
    print_section("SECTION 3: SERVICE PRE-CONFIGURATION")
    demo_service_pre_config_success()
    demo_service_pre_config_invalid_client()
    demo_service_pre_config_empty_client_id()
    
    # ========================================================================
    # Section 4: Service Installation
    # ========================================================================
    print_section("SECTION 4: SERVICE INSTALLATION")
    demo_service_install_success()
    demo_service_install_invalid_client()
    demo_service_install_missing_client_id()
    demo_service_install_empty_client_id()
    
    # ========================================================================
    # Section 5: Service Status
    # ========================================================================
    print_section("SECTION 5: SERVICE STATUS")
    demo_service_status_success()
    demo_service_status_invalid_client()
    
    # ========================================================================
    # Section 6: Health Check
    # ========================================================================
    print_section("SECTION 6: HEALTH CHECK")
    demo_health_check()
    
    # ========================================================================
    # Section 7: List Clients
    # ========================================================================
    print_section("SECTION 7: LIST CLIENTS")
    demo_list_clients()
    
    # ========================================================================
    # Section 8: Get Client Details
    # ========================================================================
    print_section("SECTION 8: GET CLIENT DETAILS")
    demo_get_client_success()
    demo_get_client_invalid()
    
    # Final summary
    print_section("DEMO COMPLETE")
    print(f"[INFO] Registered {len(TEST_CLIENTS)} test client(s)")
    print("[INFO] All test cases executed")
    print()


if __name__ == "__main__":
    main()
