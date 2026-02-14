"""
Configuration management module using Singleton pattern.

This module provides centralized configuration management for the PyArgus application,
ensuring a single instance of configuration across the entire application lifecycle.
"""

import os
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    database_url: str
    echo: bool = False
    timeout: int = 30
    
    def __post_init__(self):
        """Validate database configuration."""
        if not self.database_url:
            raise ValueError("database_url must be provided")


@dataclass
class APIConfig:
    """API server configuration settings."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 4
    
    def __post_init__(self):
        """Validate API configuration."""
        if not (0 < self.port < 65536):
            raise ValueError(f"Invalid port: {self.port}")


@dataclass
class SecurityConfig:
    """Security-related configuration settings."""
    
    encryption_key: str
    ssh_key_path: str
    authorized_keys_path: Optional[str] = None
    default_port_start: int = 9221
    default_port_end: int = 9999
    
    def __post_init__(self):
        """Validate security configuration."""
        if not self.encryption_key:
            raise ValueError("encryption_key must be provided")
        if not self.ssh_key_path:
            raise ValueError("ssh_key_path must be provided")
        if self.default_port_start >= self.default_port_end:
            raise ValueError("default_port_start must be less than default_port_end")


@dataclass
class AppConfig:
    """
    Main application configuration using Singleton pattern.
    
    Attributes:
        app_name: Name of the application
        version: Application version
        debug: Debug mode flag
        database: Database configuration
        api: API server configuration
        security: Security configuration
    """
    
    app_name: str = "PyArgus"
    version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    
    database: DatabaseConfig = field(default_factory=lambda: DatabaseConfig(
        database_url="sqlite:///pyargus.db"
    ))
    api: APIConfig = field(default_factory=APIConfig)
    security: SecurityConfig = field(default_factory=lambda: SecurityConfig(
        encryption_key="",
        ssh_key_path=""
    ))
    
    _instance: Optional["AppConfig"] = None
    
    @classmethod
    def get_instance(cls, **kwargs) -> "AppConfig":
        """
        Get or create singleton instance of AppConfig.
        
        Args:
            **kwargs: Configuration values to override defaults
            
        Returns:
            AppConfig: Singleton instance of application configuration
        """
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
    
    @staticmethod
    def from_env() -> "AppConfig":
        """
        Create AppConfig from environment variables.
        
        Returns:
            AppConfig: Configuration loaded from environment
        """
        return AppConfig(
            app_name=os.getenv("APP_NAME", "PyArgus"),
            version=os.getenv("APP_VERSION", "0.1.0"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database=DatabaseConfig(
                database_url=os.getenv(
                    "DATABASE_URL",
                    "sqlite:///pyargus.db"
                ),
                echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
            ),
            api=APIConfig(
                host=os.getenv("API_HOST", "0.0.0.0"),
                port=int(os.getenv("API_PORT", "8000")),
                debug=os.getenv("API_DEBUG", "false").lower() == "true",
                reload=os.getenv("API_RELOAD", "false").lower() == "true",
                workers=int(os.getenv("API_WORKERS", "4")),
            ),
            security=SecurityConfig(
                encryption_key=os.getenv("ENCRYPTION_KEY", ""),
                ssh_key_path=os.getenv("SSH_KEY_PATH", ""),
                authorized_keys_path=os.getenv("AUTHORIZED_KEYS_PATH"),
                default_port_start=int(os.getenv("DEFAULT_PORT_START", "9221")),
                default_port_end=int(os.getenv("DEFAULT_PORT_END", "9999")),
            ),
        )
