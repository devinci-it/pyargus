"""
API Request and Response Schemas for PyArgus.

This module defines the structure and validation for API requests and responses.
Uses basic Python dictionaries and helper functions instead of Pydantic.
"""

from typing import Dict, Any, List, Optional


class SchemaValidationError(Exception):
    """Raised when schema validation fails."""
    pass


class ClientRegistrationRequest:
    """Schema for client registration requests."""
    
    REQUIRED_FIELDS = {'hostname', 'ip_address', 'public_key'}
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate client registration request data.
        
        Args:
            data: Dictionary containing request data
            
        Returns:
            Validated data dictionary
            
        Raises:
            SchemaValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise SchemaValidationError("Request data must be a dictionary")
        
        # Check required fields
        missing = ClientRegistrationRequest.REQUIRED_FIELDS - set(data.keys())
        if missing:
            raise SchemaValidationError(f"Missing required fields: {', '.join(missing)}")
        
        # Validate field types
        if not isinstance(data['hostname'], str) or not data['hostname'].strip():
            raise SchemaValidationError("hostname must be a non-empty string")
        
        if not isinstance(data['ip_address'], str) or not data['ip_address'].strip():
            raise SchemaValidationError("ip_address must be a non-empty string")
        
        if not isinstance(data['public_key'], str) or not data['public_key'].strip():
            raise SchemaValidationError("public_key must be a non-empty string")
        
        return {
            'hostname': data['hostname'].strip(),
            'ip_address': data['ip_address'].strip(),
            'public_key': data['public_key'].strip()
        }


class ClientAuthRequest:
    """Schema for client authentication requests."""
    
    REQUIRED_FIELDS = {'client_id', 'signature', 'timestamp'}
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate client authentication request data.
        
        Args:
            data: Dictionary containing request data
            
        Returns:
            Validated data dictionary
            
        Raises:
            SchemaValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise SchemaValidationError("Request data must be a dictionary")
        
        # Check required fields
        missing = ClientAuthRequest.REQUIRED_FIELDS - set(data.keys())
        if missing:
            raise SchemaValidationError(f"Missing required fields: {', '.join(missing)}")
        
        # Validate field types
        if not isinstance(data['client_id'], str) or not data['client_id'].strip():
            raise SchemaValidationError("client_id must be a non-empty string")
        
        if not isinstance(data['signature'], str) or not data['signature'].strip():
            raise SchemaValidationError("signature must be a non-empty string")
        
        if not isinstance(data['timestamp'], int) or data['timestamp'] <= 0:
            raise SchemaValidationError("timestamp must be a positive integer")
        
        return {
            'client_id': data['client_id'].strip(),
            'signature': data['signature'].strip(),
            'timestamp': data['timestamp']
        }


class ServiceInstallRequest:
    """Schema for service installation requests."""
    
    REQUIRED_FIELDS = {'client_id'}
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate service installation request data.
        
        Args:
            data: Dictionary containing request data
            
        Returns:
            Validated data dictionary
            
        Raises:
            SchemaValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise SchemaValidationError("Request data must be a dictionary")
        
        # Check required fields
        missing = ServiceInstallRequest.REQUIRED_FIELDS - set(data.keys())
        if missing:
            raise SchemaValidationError(f"Missing required fields: {', '.join(missing)}")
        
        if not isinstance(data['client_id'], str) or not data['client_id'].strip():
            raise SchemaValidationError("client_id must be a non-empty string")
        
        return {
            'client_id': data['client_id'].strip()
        }


class ClientRegistrationResponse:
    """Schema for client registration responses."""
    
    @staticmethod
    def build(client_id: str, assigned_port: int, message: str = "Client registered successfully") -> Dict[str, Any]:
        """
        Build a client registration response.
        
        Args:
            client_id: The registered client ID
            assigned_port: The assigned remote port
            message: Optional response message
            
        Returns:
            Response dictionary
        """
        return {
            'status': 'success',
            'client_id': client_id,
            'assigned_port': assigned_port,
            'message': message
        }


class ServiceInstallResponse:
    """Schema for service installation responses."""
    
    @staticmethod
    def build(service_file_content: str, assigned_port: int) -> Dict[str, Any]:
        """
        Build a service installation response.
        
        Args:
            service_file_content: The systemd service file content
            assigned_port: The assigned remote port
            
        Returns:
            Response dictionary
        """
        return {
            'status': 'success',
            'service_file_content': service_file_content,
            'assigned_port': assigned_port,
            'message': "Service file generated successfully"
        }


class ServicePreConfigResponse:
    """Schema for service pre-configuration responses."""
    
    @staticmethod
    def build(client_id: str, assigned_port: int, hostname: str, ip_address: str) -> Dict[str, Any]:
        """
        Build a service pre-configuration response.
        
        Args:
            client_id: The client ID
            assigned_port: The assigned remote port
            hostname: The client hostname
            ip_address: The client IP address
            
        Returns:
            Response dictionary
        """
        return {
            'status': 'success',
            'client_id': client_id,
            'assigned_port': assigned_port,
            'hostname': hostname,
            'ip_address': ip_address,
            'message': "Service pre-configuration successful"
        }


class ServiceStatusResponse:
    """Schema for service status responses."""
    
    @staticmethod
    def build(client_id: str, status: str, assigned_port: int, tunnel_active: bool) -> Dict[str, Any]:
        """
        Build a service status response.
        
        Args:
            client_id: The client ID
            status: The service status (active, inactive, error)
            assigned_port: The assigned remote port
            tunnel_active: Whether the tunnel is currently active
            
        Returns:
            Response dictionary
        """
        return {
            'status': status,
            'client_id': client_id,
            'assigned_port': assigned_port,
            'tunnel_active': tunnel_active,
            'message': f"Tunnel status is {status}"
        }


class HealthCheckResponse:
    """Schema for health check responses."""
    
    @staticmethod
    def build(version: str = "0.1.0") -> Dict[str, Any]:
        """
        Build a health check response.
        
        Args:
            version: The application version
            
        Returns:
            Response dictionary
        """
        return {
            'status': 'healthy',
            'version': version,
            'message': 'PyArgus API is running',
            'services': {
                'database': 'connected',
                'ssh_manager': 'ready',
                'security': 'ready'
            }
        }


class ErrorResponse:
    """Schema for error responses."""
    
    @staticmethod
    def build(error_code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build an error response.
        
        Args:
            error_code: The error code (e.g., 'INVALID_REQUEST', 'NOT_FOUND', 'SERVER_ERROR')
            message: The error message
            details: Optional additional error details
            
        Returns:
            Response dictionary
        """
        response = {
            'status': 'error',
            'error_code': error_code,
            'message': message
        }
        
        if details:
            response['details'] = details
        
        return response
