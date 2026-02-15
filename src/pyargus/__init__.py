"""
PyArgus Application Package.

Main entry point for the PyArgus SSH Bastion application.
Exports the core classes and functions for public API.
"""

from .core.config import AppConfig, DatabaseConfig, APIConfig, SecurityConfig
from .core.exceptions import (
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
from .core.context import AppContext, ctx
from .core.paths import get_app_data_dir, get_logs_dir, get_cache_dir, get_config_dir
from .app import PyArgusApp, get_app, initialize_app, app, main

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
    "build_log_decorator",
    "SettingsBuilder",
    "SUCCESS_LEVEL",
    "register_success_level",
    # Global Context
    "AppContext",
    "ctx",
    # Central App Module
    "PyArgusApp",
    "get_app",
    "initialize_app",
    "main",
    "app",
]
