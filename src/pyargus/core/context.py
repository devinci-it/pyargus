"""
Application Context - Single point of access for globals.

This provides clean, dependency-injection-free access to:
- Logger singleton
- Application instance
- Configuration
- Services

Usage anywhere in the app:
    from pyargus.core.context import ctx
    
    # Access logger
    ctx.logger.info("Message")
    
    # Access config
    print(ctx.config.app_name)
    
    # Access app
    ctx.app.shutdown()
    
    # Access services
    service = ctx.get_service('service_name')
"""

from typing import Optional, Any


class AppContext:
    """
    Global application context for singleton access.
    
    Stores references to:
    - PyLogger singleton instance
    - Application instance
    - Configuration
    
    Access via: from pyargus.core.context import ctx
    """
    
    _logger: Optional[Any] = None
    _config: Optional[Any] = None
    _app: Optional[Any] = None
    
    @classmethod
    def initialize(cls, logger=None, config=None, app=None):
        """
        Initialize the application context during bootstrap.
        
        Args:
            logger: PyLogger instance
            config: AppConfig instance
            app: Application instance
        """
        cls._logger = logger
        cls._config = config
        cls._app = app
    
    @classmethod
    def logger(cls):
        """Get the PyLogger singleton instance."""
        if cls._logger is None:
            # Import PyLogger singleton, not the wrapper
            from pylogger import Logger as PyLogger
            cls._logger = PyLogger.instance()
        return cls._logger
    
    @classmethod
    def config(cls):
        """Get the AppConfig singleton instance."""
        if cls._config is None:
            from .config import AppConfig
            # Use from_env() to load from environment (required for singleton)
            cls._config = AppConfig.from_env()
        return cls._config
    
    @classmethod
    def app(cls):
        """Get the Application singleton instance."""
        if cls._app is None:
            from ..application import ApplicationFactory
            cls._app = ApplicationFactory.get_instance()
        return cls._app
    
    @classmethod
    def get_service(cls, service_name: str) -> Any:
        """
        Get a service from the DependencyContainer.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            The service instance
        """
        return cls.app()._container.get(service_name)
    
    @classmethod
    def reset(cls):
        """Reset the context (useful for testing)."""
        cls._logger = None
        cls._config = None
        cls._app = None


# Create a convenience singleton instance
ctx = AppContext()


__all__ = [
    "AppContext",
    "ctx",
]
