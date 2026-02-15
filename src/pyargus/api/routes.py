"""
API Routes for PyArgus.

This module defines the Flask routes/endpoints for the PyArgus API.
Handles HTTP requests and returns JSON responses.
"""

from flask import Blueprint, request, jsonify
import json
import logging
from typing import Tuple

from . import schemas, handlers

# Configure logger for request auditing
logger = logging.getLogger(__name__)


# Create Blueprint for API routes
api_blueprint = Blueprint('api', __name__, url_prefix='/api')


def _get_json_data() -> dict:
    """
    Get JSON data from request.
    
    Returns:
        Request JSON data as dictionary
        
    Raises:
        ValueError: If request contains invalid JSON
    """
    try:
        if not request.is_json:
            raise ValueError("Content-Type must be application/json")
        
        data = request.get_json()
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        
        return data
    except ValueError as e:
        raise ValueError(f"Invalid request: {str(e)}")


def _handle_response(response_data: dict, status_code: int) -> Tuple:
    """
    Format response and status code for Flask.
    
    Args:
        response_data: Response data dictionary
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    return jsonify(response_data), status_code


# ============================================================================
# Client Registration Endpoint
# ============================================================================

@api_blueprint.route('/register', methods=['POST'])
def register():
    """
    Register a new client.
    
    Request body:
    {
        "hostname": "client.example.com",
        "ip_address": "192.168.1.100",
        "public_key": "ssh-rsa AAAA... user@host"
    }
    
    Response (201):
    {
        "status": "success",
        "client_id": "uuid-string",
        "assigned_port": 9221,
        "message": "Client registered successfully"
    }
    
    Response (409):
    {
        "status": "error",
        "error_code": "DUPLICATE_CLIENT",
        "message": "Public key already registered"
    }
    """
    try:
        logger.info(f"[AUDIT] {request.method} {request.path} from {request.remote_addr}")
        
        # Get request data
        data = _get_json_data()
        
        # Validate request
        validated_data = schemas.ClientRegistrationRequest.validate(data)
        
        # Handle registration
        response_data, status_code = handlers.handle_client_registration(validated_data)
        
        logger.info(f"[AUDIT] Response: {status_code} | {response_data.get('status', 'unknown')}")
        
        return _handle_response(response_data, status_code)
        
    except schemas.SchemaValidationError as e:
        logger.warning(f"[AUDIT] Schema validation error: {str(e)}")
        error_response = schemas.ErrorResponse.build(
            'INVALID_REQUEST',
            str(e)
        )
        return _handle_response(error_response, 400)
        
    except ValueError as e:
        logger.warning(f"[AUDIT] JSON parsing error: {str(e)}")
        error_response = schemas.ErrorResponse.build(
            'INVALID_JSON',
            str(e)
        )
        return _handle_response(error_response, 400)
        
    except Exception as e:
        logger.error(f"[AUDIT] Unexpected error: {str(e)}", exc_info=True)
        error_response = schemas.ErrorResponse.build(
            'SERVER_ERROR',
            f'Registration failed: {str(e)}'
        )
        return _handle_response(error_response, 500)


# ============================================================================
# Authentication Endpoint
# ============================================================================

@api_blueprint.route('/auth', methods=['POST'])
def authenticate():
    """
    Authenticate a client.
    
    Request body:
    {
        "client_id": "uuid-string",
        "signature": "signature-data",
        "timestamp": 1676500000
    }
    
    Response (200):
    {
        "status": "success",
        "authenticated": true,
        "client_id": "uuid-string",
        "message": "Client authenticated successfully"
    }
    
    Response (401):
    {
        "status": "error",
        "error_code": "INVALID_SIGNATURE",
        "message": "Invalid signature format"
    }
    """
    try:
        logger.info(f"[AUDIT] {request.method} {request.path} from {request.remote_addr}")
        
        # Get request data
        data = _get_json_data()
        
        # Validate request
        validated_data = schemas.ClientAuthRequest.validate(data)
        
        # Handle authentication
        response_data, status_code = handlers.handle_authentication(validated_data)
        
        logger.info(f"[AUDIT] Response: {status_code} | client_id={validated_data.get('client_id')}")
        
        return _handle_response(response_data, status_code)
        
    except schemas.SchemaValidationError as e:
        logger.warning(f"[AUDIT] Schema validation error: {str(e)}")
        error_response = schemas.ErrorResponse.build(
            'INVALID_REQUEST',
            str(e)
        )
        return _handle_response(error_response, 400)
        
    except ValueError as e:
        logger.warning(f"[AUDIT] JSON parsing error: {str(e)}")
        error_response = schemas.ErrorResponse.build(
            'INVALID_JSON',
            str(e)
        )
        return _handle_response(error_response, 400)
        
    except Exception as e:
        logger.error(f"[AUDIT] Unexpected error: {str(e)}", exc_info=True)
        error_response = schemas.ErrorResponse.build(
            'SERVER_ERROR',
            f'Authentication failed: {str(e)}'
        )
        return _handle_response(error_response, 500)


# ============================================================================
# Service Pre-Configuration Endpoint
# ============================================================================

@api_blueprint.route('/service/pre/<client_id>', methods=['GET'])
def service_pre_config(client_id: str):
    """
    Get pre-configuration for service installation.
    
    URL parameter:
        client_id: The client ID
    
    Response (200):
    {
        "status": "success",
        "client_id": "uuid-string",
        "assigned_port": 9221,
        "hostname": "client.example.com",
        "ip_address": "192.168.1.100",
        "message": "Service pre-configuration successful"
    }
    
    Response (404):
    {
        "status": "error",
        "error_code": "CLIENT_NOT_FOUND",
        "message": "Client uuid-string not found"
    }
    """
    try:
        # Handle pre-configuration
        response_data, status_code = handlers.handle_service_pre_config(client_id)
        
        return _handle_response(response_data, status_code)
        
    except Exception as e:
        error_response = schemas.ErrorResponse.build(
            'SERVER_ERROR',
            f'Pre-configuration failed: {str(e)}'
        )
        return _handle_response(error_response, 500)


# ============================================================================
# Service Installation Endpoint
# ============================================================================

@api_blueprint.route('/service/install', methods=['POST'])
def service_install():
    """
    Generate and return systemd service file for installation.
    
    Request body:
    {
        "client_id": "uuid-string"
    }
    
    Response (200):
    {
        "status": "success",
        "service_file_content": "[Unit]\\nDescription=...",
        "assigned_port": 9221,
        "message": "Service file generated successfully"
    }
    
    Response (404):
    {
        "status": "error",
        "error_code": "CLIENT_NOT_FOUND",
        "message": "Client uuid-string not found"
    }
    """
    try:
        # Get request data
        data = _get_json_data()
        
        # Validate request
        validated_data = schemas.ServiceInstallRequest.validate(data)
        
        # Handle service installation
        response_data, status_code = handlers.handle_service_install(validated_data)
        
        return _handle_response(response_data, status_code)
        
    except schemas.SchemaValidationError as e:
        error_response = schemas.ErrorResponse.build(
            'INVALID_REQUEST',
            str(e)
        )
        return _handle_response(error_response, 400)
        
    except ValueError as e:
        error_response = schemas.ErrorResponse.build(
            'INVALID_JSON',
            str(e)
        )
        return _handle_response(error_response, 400)
        
    except Exception as e:
        error_response = schemas.ErrorResponse.build(
            'SERVER_ERROR',
            f'Service generation failed: {str(e)}'
        )
        return _handle_response(error_response, 500)


# ============================================================================
# Service Status Endpoint
# ============================================================================

@api_blueprint.route('/service/status/<client_id>', methods=['GET'])
def service_status(client_id: str):
    """
    Check service/tunnel status for a client.
    
    URL parameter:
        client_id: The client ID
    
    Response (200):
    {
        "status": "active",
        "client_id": "uuid-string",
        "assigned_port": 9221,
        "tunnel_active": true,
        "message": "Tunnel status is active"
    }
    
    Response (404):
    {
        "status": "error",
        "error_code": "CLIENT_NOT_FOUND",
        "message": "Client uuid-string not found"
    }
    """
    try:
        # Handle status check
        response_data, status_code = handlers.handle_service_status(client_id)
        
        return _handle_response(response_data, status_code)
        
    except Exception as e:
        error_response = schemas.ErrorResponse.build(
            'SERVER_ERROR',
            f'Status check failed: {str(e)}'
        )
        return _handle_response(error_response, 500)


# ============================================================================
# Health Check Endpoint
# ============================================================================

@api_blueprint.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Response (200):
    {
        "status": "healthy",
        "version": "0.1.0",
        "message": "PyArgus API is running",
        "services": {
            "database": "connected",
            "ssh_manager": "ready",
            "security": "ready"
        }
    }
    """
    try:
        logger.debug(f"[AUDIT] {request.method} {request.path} from {request.remote_addr}")
        
        # Handle health check
        response_data, status_code = handlers.handle_health_check()
        
        return _handle_response(response_data, status_code)
        
    except Exception as e:
        logger.error(f"[AUDIT] Health check error: {str(e)}", exc_info=True)
        error_response = schemas.ErrorResponse.build(
            'SERVER_ERROR',
            f'Health check failed: {str(e)}'
        )
        return _handle_response(error_response, 500)


# ============================================================================
# Admin: List Clients Endpoint
# ============================================================================

@api_blueprint.route('/clients', methods=['GET'])
def list_clients():
    """
    List all registered clients (admin endpoint).
    
    Query parameters:
        limit: Maximum number of clients to return (optional)
        offset: Number of clients to skip (optional)
    
    Response (200):
    {
        "status": "success",
        "clients": [
            {
                "client_id": "uuid-string",
                "hostname": "client.example.com",
                "ip_address": "192.168.1.100",
                "assigned_port": 9221,
                "created_at": "2024-02-14T10:00:00",
                "status": "registered",
                "tunnel_active": false
            },
            ...
        ],
        "total": 1,
        "message": "Clients retrieved successfully"
    }
    """
    try:
        # Handle list clients
        response_data, status_code = handlers.handle_list_clients()
        
        return _handle_response(response_data, status_code)
        
    except Exception as e:
        error_response = schemas.ErrorResponse.build(
            'SERVER_ERROR',
            f'Failed to retrieve clients: {str(e)}'
        )
        return _handle_response(error_response, 500)


# ============================================================================
# Get Client Details Endpoint
# ============================================================================

@api_blueprint.route('/clients/<client_id>', methods=['GET'])
def get_client(client_id: str):
    """
    Get details for a specific client.
    
    URL parameter:
        client_id: The client ID
    
    Response (200):
    {
        "status": "success",
        "client": {
            "client_id": "uuid-string",
            "hostname": "client.example.com",
            "ip_address": "192.168.1.100",
            "assigned_port": 9221,
            "created_at": "2024-02-14T10:00:00",
            "status": "registered",
            "tunnel_active": false
        },
        "message": "Client retrieved successfully"
    }
    
    Response (404):
    {
        "status": "error",
        "error_code": "CLIENT_NOT_FOUND",
        "message": "Client uuid-string not found"
    }
    """
    try:
        # Get client
        client = handlers.ClientRegistry.get_client(client_id)
        if not client:
            error_response = schemas.ErrorResponse.build(
                'CLIENT_NOT_FOUND',
                f'Client {client_id} not found'
            )
            return _handle_response(error_response, 404)
        
        response_data = {
            'status': 'success',
            'client': client,
            'message': 'Client retrieved successfully'
        }
        
        return _handle_response(response_data, 200)
        
    except Exception as e:
        error_response = schemas.ErrorResponse.build(
            'SERVER_ERROR',
            f'Failed to retrieve client: {str(e)}'
        )
        return _handle_response(error_response, 500)
