"""
PyArgus Central Application Module.

This is the main entry point for the PyArgus application.
It provides a centralized access point to:
- Application context (logger, config, services)
- Core utilities and helpers
- Application lifecycle management
"""

import logging
import sys
import argparse
from typing import Optional, Callable, Any, Dict
from functools import wraps

from .core.bootstrap import Bootstrap
from .core.config import AppConfig
from .core.context import AppContext, ctx
from .core.exceptions import ConfigurationError


class PyArgusApp:
    """
    Central PyArgus application wrapper.
    
    Provides unified access to:
    - Logger
    - Configuration
    - Application context
    - Core services
    - Utilities and helpers
    """
    
    def __init__(self):
        """Initialize PyArgus application."""
        self.bootstrap: Optional[Bootstrap] = None
        self._initialized: bool = False
        self._services: Dict[str, Any] = {}
    
    @property
    def logger(self) -> logging.Logger:
        """Get application logger."""
        if self.bootstrap is None or self.bootstrap.logger is None:
            raise RuntimeError("Application not initialized. Call app.initialize() first.")
        return self.bootstrap.logger
    
    @property
    def config(self) -> AppConfig:
        """Get application configuration."""
        if self.bootstrap is None or self.bootstrap.config is None:
            raise RuntimeError("Application not initialized. Call app.initialize() first.")
        return self.bootstrap.config
    
    @property
    def context(self) -> AppContext:
        """Get application context."""
        if self.bootstrap is None or self.bootstrap.app_context is None:
            raise RuntimeError("Application not initialized. Call app.initialize() first.")
        return self.bootstrap.app_context
    
    @property
    def is_initialized(self) -> bool:
        """Check if application is initialized."""
        return self._initialized and self.bootstrap and self.bootstrap.is_initialized
    
    @property
    def services(self) -> Dict[str, Any]:
        """Get all registered services."""
        return self._services.copy()
    
    def initialize(self, debug: bool = False) -> "PyArgusApp":
        """
        Initialize the application with full bootstrapping.
        
        Args:
            debug: Enable debug mode
            
        Returns:
            PyArgusApp: Self for chaining
            
        Raises:
            ConfigurationError: If initialization fails
        """
        if self._initialized:
            self.logger.debug("Application already initialized, skipping")
            return self
        
        # Run bootstrap
        self.bootstrap = Bootstrap.get_instance()
        self.bootstrap.bootstrap(debug=debug)
        
        self._initialized = True
        self.logger.info("PyArgus application initialized successfully")
        
        return self
    
    def register_service(self, name: str, service: Any) -> None:
        """
        Register a service for later access.
        
        Args:
            name: Service name
            service: Service instance or callable
        """
        self._services[name] = service
        self.logger.debug(f"Service registered: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """
        Get a registered service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance or None if not found
        """
        return self._services.get(name)
    
    def shutdown(self) -> None:
        """Shutdown the application and cleanup resources."""
        if not self._initialized:
            return
        
        self.logger.info("Shutting down PyArgus application")
        
        if self.bootstrap and self.bootstrap.app:
            self.bootstrap.app.shutdown()
        
        self._initialized = False
        self.logger.info("PyArgus application shutdown completed")
    
    # =========================================================================
    # Utility Methods / Helpers
    # =========================================================================
    
    def log_decorator(self, func: Callable) -> Callable:
        """
        Decorator to log function calls.
        
        Usage:
            @app.log_decorator
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.debug(f"Calling {func.__name__}")
            try:
                result = func(*args, **kwargs)
                self.logger.debug(f"Completed {func.__name__}")
                return result
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
    
    def get_db_connection(self):
        """
        Get database connection from context.
        
        Returns:
            Database connection or None
        """
        if hasattr(self.context, 'db'):
            return self.context.db
        return None
    
    def __repr__(self) -> str:
        """String representation of the app."""
        status = "initialized" if self.is_initialized else "not initialized"
        if self.is_initialized:
            return (
                f"PyArgusApp({status}, "
                f"env={self.config.environment}, "
                f"debug={self.config.debug})"
            )
        return f"PyArgusApp({status})"


# Singleton instance - create once at module load
_app_instance: Optional[PyArgusApp] = None


def get_app() -> PyArgusApp:
    """
    Get the global PyArgus application instance.
    
    Returns:
        PyArgusApp: Global application instance
    
    Usage:
        from pyargus.app import get_app
        app = get_app()
        logger = app.logger
        config = app.config
    """
    global _app_instance
    if _app_instance is None:
        _app_instance = PyArgusApp()
    return _app_instance


def initialize_app(debug: bool = False) -> PyArgusApp:
    """
    Initialize the global PyArgus application.
    
    Args:
        debug: Enable debug mode
        
    Returns:
        PyArgusApp: Initialized application instance
    
    Usage:
        from pyargus.app import initialize_app
        app = initialize_app(debug=True)
    """
    app = get_app()
    return app.initialize(debug=debug)


# Export convenience instance
app = get_app()


# ============================================================================
# Console Script Entry Point
# ============================================================================

def main() -> int:
    """
    Main entry point for PyArgus CLI.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="PyArgus SSH Bastion Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="API server port (override config)"
    )
    parser.add_argument(
        "--host",
        help="API server host (override config)"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version"
    )
    
    try:
        args = parser.parse_args()
        
        if args.version:
            print("PyArgus version 0.1.0")
            return 0
        
        # Initialize app
        app_instance = initialize_app(debug=args.debug)
        
        # Override config from CLI args if provided
        if args.port:
            app_instance.config.api.port = args.port
        
        if args.host:
            app_instance.config.api.host = args.host
        
        # Log startup info
        app_instance.logger.info(f"PyArgus starting in {app_instance.config.environment} mode")
        print("✓ Application initialized successfully")
        print(f"\nAPI Server is listening at http://{app_instance.config.api.host}:{app_instance.config.api.port}")
        print("\nPress Ctrl+C to stop the server\n")
        
        # TODO: Start actual server here (uvicorn, Django, etc.)
        # For now, just keep running until interrupted
        
        return 0
        
    except ConfigurationError as e:
        print(f"\n❌ Configuration Error: {e.message}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        try:
            app_instance.logger.info("Shutdown signal received")
            app_instance.shutdown()
        except:
            pass
        print("\n✓ Application shutdown completed")
        return 0
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}", file=sys.stderr)
        return 1
