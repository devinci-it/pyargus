"""
PyArgus Application Bootstrap Module.

This module provides the main application bootstrap and dependency injection
container using the Factory pattern. It serves as the single entry point for
initializing all application components.
"""

import logging
from typing import Optional, List
from abc import ABC, abstractmethod

from .config import AppConfig
from .exceptions import ConfigurationError


class ILogger(ABC):
    """Abstract interface for logging."""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        pass
    
    @abstractmethod
    def error(self, message: str, exception: Exception = None, **kwargs) -> None:
        """Log error message."""
        pass


class Logger(ILogger):
    """Concrete implementation of ILogger using Python's logging module."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """
        Initialize logger.
        
        Args:
            name: Logger name (usually __name__ of the module)
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper()))
        
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, exception: Exception = None, **kwargs) -> None:
        """Log error message with optional exception."""
        if exception:
            self._logger.error(message, exc_info=True, **kwargs)
        else:
            self._logger.error(message, **kwargs)


class IDependencyContainer(ABC):
    """Abstract interface for dependency container."""
    
    @abstractmethod
    def get(self, service_name: str):
        """Get a service from the container."""
        pass
    
    @abstractmethod
    def register(self, service_name: str, instance) -> None:
        """Register a service in the container."""
        pass


class DependencyContainer(IDependencyContainer):
    """
    Simple dependency injection container using Registry pattern.
    
    Manages singleton instances of application services and provides
    a centralized way to access them throughout the application.
    """
    
    def __init__(self):
        """Initialize empty service registry."""
        self._services = {}
        self._logger = logging.getLogger(__name__)
    
    def register(self, service_name: str, instance) -> None:
        """
        Register a service in the container.
        
        Args:
            service_name: Name to register the service under
            instance: The service instance to register
            
        Raises:
            ConfigurationError: If service is already registered
        """
        if service_name in self._services:
            raise ConfigurationError(
                f"Service '{service_name}' is already registered"
            )
        
        self._services[service_name] = instance
        self._logger.debug(f"Registered service: {service_name}")
    
    def get(self, service_name: str):
        """
        Get a service from the container.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            The requested service instance
            
        Raises:
            ConfigurationError: If service is not registered
        """
        if service_name not in self._services:
            raise ConfigurationError(
                f"Service '{service_name}' is not registered in the container"
            )
        
        return self._services[service_name]
    
    def has(self, service_name: str) -> bool:
        """Check if a service is registered."""
        return service_name in self._services


class Application:
    """
    Main PyArgus Application class.
    
    Serves as the single entry point for the entire application, coordinating
    initialization of all components, configuration loading, and dependency
    injection container setup.
    
    Uses the Factory pattern and Dependency Injection for loose coupling and
    better testability.
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize the application.
        
        Args:
            config: Application configuration. If not provided, loads from environment.
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        self._config = config or AppConfig.from_env()
        self._container = DependencyContainer()
        self._logger = Logger(
            self.__class__.__name__,
            self._config.log_level
        )
        self._is_initialized = False
        
        self._logger.info(
            f"Initializing {self._config.app_name} v{self._config.version} "
            f"in {self._config.environment} mode"
        )
        
        # Validate configuration immediately
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """
        Validate application configuration.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Check critical configuration values
            if not self._config.security.encryption_key:
                raise ConfigurationError(
                    "ENCRYPTION_KEY must be set in environment or config"
                )
            if not self._config.security.ssh_key_path:
                raise ConfigurationError(
                    "SSH_KEY_PATH must be set in environment or config"
                )
            
            self._logger.info("Configuration validation successful")
        except Exception as e:
            self._logger.error(f"Configuration validation failed: {str(e)}", e)
            raise
    
    def initialize(self) -> "Application":
        """
        Initialize all application components.
        
        This method sets up the dependency container with all services
        and prepares the application for use.
        
        Returns:
            Application: Self for method chaining
            
        Raises:
            ConfigurationError: If initialization fails
        """
        if self._is_initialized:
            self._logger.warning("Application already initialized, skipping re-initialization")
            return self
        
        try:
            self._logger.info("Starting application initialization...")
            
            # Register core services in the container
            self._register_core_services()
            
            # Initialize sub-components
            self._initialize_components()
            
            self._is_initialized = True
            self._logger.info("Application initialization completed successfully")
            
        except Exception as e:
            self._logger.error("Application initialization failed", e)
            raise ConfigurationError(f"Failed to initialize application: {str(e)}")
        
        return self
    
    def _register_core_services(self) -> None:
        """
        Register core application services in the dependency container.
        
        This includes configuration, logger, and other fundamental services.
        """
        self._logger.debug("Registering core services...")
        
        # Register configuration
        self._container.register("config", self._config)
        
        # Register logger
        self._container.register("logger", self._logger)
        
        # Register dependency container itself (for services that need it)
        self._container.register("container", self._container)
    
    def _initialize_components(self) -> None:
        """
        Initialize application components/modules.
        
        This method will be extended to initialize specific components
        (database, API, SSH manager, etc.) as they are implemented.
        """
        self._logger.debug("Initializing components...")
        # TODO: Initialize database, API, SSH manager, etc.
    
    @property
    def config(self) -> AppConfig:
        """Get application configuration."""
        return self._config
    
    @property
    def container(self) -> IDependencyContainer:
        """Get dependency injection container."""
        return self._container
    
    @property
    def logger(self) -> ILogger:
        """Get application logger."""
        return self._logger
    
    @property
    def is_initialized(self) -> bool:
        """Check if application is initialized."""
        return self._is_initialized
    
    def shutdown(self) -> None:
        """
        Gracefully shutdown the application.
        
        Cleanup resources and close connections.
        """
        self._logger.info("Shutting down application...")
        # TODO: Implement cleanup logic
        self._is_initialized = False
        self._logger.info("Application shutdown completed")


class ApplicationFactory:
    """
    Factory for creating and managing Application instances.
    
    Uses the Factory pattern to provide a clean interface for
    application creation and lifecycle management.
    """
    
    _instance: Optional[Application] = None
    _logger = logging.getLogger(__name__)
    
    @classmethod
    def create(cls, config: Optional[AppConfig] = None) -> Application:
        """
        Create and initialize a new Application instance.
        
        Args:
            config: Optional AppConfig instance
            
        Returns:
            Application: Initialized application instance
        """
        app = Application(config)
        app.initialize()
        return app
    
    @classmethod
    def get_instance(cls) -> Optional[Application]:
        """
        Get the current application instance (if any).
        
        Returns:
            Application or None if not created yet
        """
        return cls._instance
    
    @classmethod
    def set_instance(cls, app: Application) -> None:
        """
        Set the current application instance.
        
        Args:
            app: Application instance to set
        """
        cls._instance = app


# Global logger for module-level operations
_module_logger = Logger(__name__)
