"""
PyArgus Application Package.

Main entry point for the PyArgus SSH Bastion application.
Exports the core classes and functions for public API.
"""

from .config import AppConfig, DatabaseConfig, APIConfig, SecurityConfig
from .exceptions import (
    PyArgusException,
    ConfigurationError,
    DatabaseError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    SSHError,
    EncryptionError,
    ResourceNotFoundError,
    ResourceConflictError,
)
from .application import (
    Application,
    ApplicationFactory,
    Logger,
    DependencyContainer,
    ILogger,
    IDependencyContainer,
)
from .logging_config import LoggerConfigurator

# PyLogger decorators and utilities
from pylogger import (
    build_log_decorator,
    SettingsBuilder,
    SUCCESS_LEVEL,
    register_success_level,
)

__version__ = "0.1.0"
__author__ = "PyArgus Team"
__all__ = [
    # Configuration
    "AppConfig",
    "DatabaseConfig",
    "APIConfig",
    "SecurityConfig",
    # Exceptions
    "PyArgusException",
    "ConfigurationError",
    "DatabaseError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "SSHError",
    "EncryptionError",
    "ResourceNotFoundError",
    "ResourceConflictError",
    # Application
    "Application",
    "ApplicationFactory",
    "Logger",
    "DependencyContainer",
    "ILogger",
    "IDependencyContainer",
    # Logging
    "LoggerConfigurator",
    "build_log_decorator",
    "SettingsBuilder",
    "SUCCESS_LEVEL",
    "register_success_level",
]
