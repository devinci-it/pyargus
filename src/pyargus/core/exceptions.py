"""
Custom exceptions for PyArgus application.

Defines application-specific exception hierarchy for better error handling
and domain-specific error communication.
"""


class PyArgusException(Exception):
    """Base exception for all PyArgus-specific errors."""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        """
        Initialize PyArgusException.
        
        Args:
            message: Descriptive error message
            error_code: Unique error code for programmatic handling
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ConfigurationError(PyArgusException):
    """Raised when application configuration is invalid."""
    
    def __init__(self, message: str, error_code: str = "CONFIG_ERROR"):
        super().__init__(message, error_code)


class DatabaseError(PyArgusException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class ValidationError(PyArgusException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


class AuthenticationError(PyArgusException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class AuthorizationError(PyArgusException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, "AUTHZ_ERROR")


class SSHError(PyArgusException):
    """Raised when SSH operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "SSH_ERROR")


class EncryptionError(PyArgusException):
    """Raised when encryption/decryption operations fail."""
    
    def __init__(self, message: str):
        super().__init__(message, "ENCRYPTION_ERROR")


class ResourceNotFoundError(PyArgusException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, "NOT_FOUND")


class ResourceConflictError(PyArgusException):
    """Raised when a resource already exists."""
    
    def __init__(self, resource_type: str, resource_identifier: str):
        message = f"{resource_type} already exists: {resource_identifier}"
        super().__init__(message, "CONFLICT")
