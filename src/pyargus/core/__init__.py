"""
PyArgus Core Module - Central configuration and bootstrap infrastructure.

This module provides:
- Configuration management (config.py)
- Exception hierarchy (exceptions.py)
- Application context (context.py)
- Bootstrap initialization (bootstrap.py)
- Path management (paths.py)
- Database ORM and models (database.py, models.py)
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
from .context import AppContext, ctx
from .bootstrap import Bootstrap
from .paths import get_app_data_dir, get_logs_dir, get_cache_dir, get_config_dir
from .database import get_database, init_database, close_database, create_tables, BaseModel
from .models import Client, SSHKey, TunnelAssignment, ServiceStatus

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
    # Context
    "AppContext",
    "ctx",
    # Bootstrap
    "Bootstrap",
    # Paths
    "get_app_data_dir",
    "get_logs_dir",
    "get_cache_dir",
    "get_config_dir",
    # Database
    "get_database",
    "init_database",
    "close_database",
    "create_tables",
    "BaseModel",
    # Models
    "Client",
    "SSHKey",
    "TunnelAssignment",
    "ServiceStatus",
]
