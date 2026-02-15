"""
PyArgus Bootstrap Module.

Handles all application initialization, context setup, and configuration loading.
This module sets up the application context and all core components that will be
exposed through the app.py central entry point.
"""

import os
import logging
import sys
from typing import Optional
from dotenv import load_dotenv

from .config import AppConfig
from .context import AppContext, ctx
from ..application import ApplicationFactory
from .exceptions import ConfigurationError


class Bootstrap:
    """
    Bootstrap handler for PyArgus application initialization.
    
    Responsible for:
    - Loading environment variables
    - Initializing configuration
    - Setting up logging
    - Creating application context
    - Initializing core services
    """
    
    _instance: Optional["Bootstrap"] = None
    _initialized: bool = False
    
    def __init__(self):
        """Initialize Bootstrap singleton."""
        self.config: Optional[AppConfig] = None
        self.app_context: Optional[AppContext] = None
        self.logger: Optional[logging.Logger] = None
        self.app = None
        
    @classmethod
    def get_instance(cls) -> "Bootstrap":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset singleton (useful for testing)."""
        cls._instance = None
        cls._initialized = False
    
    def load_environment(self) -> None:
        """
        Load environment variables from .env file if it exists.
        
        Raises:
            ConfigurationError: If environment loading fails
        """
        try:
            if os.path.exists('.env'):
                load_dotenv('.env')
                print("✓ Loaded environment from .env")
            else:
                print("ℹ No .env file found, using system environment")
        except Exception as e:
            raise ConfigurationError(
                message=f"Failed to load environment: {str(e)}",
                error_code="ENV_LOAD_FAILED"
            )
    
    def setup_logging(self, debug: bool = False) -> logging.Logger:
        """
        Setup basic logging using Python's built-in logging module.
        
        Args:
            debug: Enable debug level logging
            
        Returns:
            logging.Logger: Configured logger instance
        """
        log_level = logging.DEBUG if debug else logging.INFO
        log_level_str = os.getenv('PYARGUS_LOG_LEVEL', 'INFO')
        
        try:
            log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        except (AttributeError, ValueError):
            log_level = logging.INFO
        
        if debug:
            log_level = logging.DEBUG
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
            ]
        )
        
        logger = logging.getLogger('pyargus')
        self.logger = logger
        return logger
    
    def load_configuration(self) -> AppConfig:
        """
        Load application configuration from environment.
        
        Returns:
            AppConfig: Loaded configuration singleton
            
        Raises:
            ConfigurationError: If configuration loading fails
        """
        try:
            config = AppConfig.get_instance()
            
            # Override from environment if provided
            if os.getenv('PYARGUS_DEBUG'):
                config.debug = os.getenv('PYARGUS_DEBUG', '').lower() == 'true'
            
            if os.getenv('PYARGUS_ENVIRONMENT'):
                config.environment = os.getenv('PYARGUS_ENVIRONMENT')
            
            if os.getenv('PYARGUS_API_HOST'):
                config.api.host = os.getenv('PYARGUS_API_HOST')
            
            if os.getenv('PYARGUS_API_PORT'):
                config.api.port = int(os.getenv('PYARGUS_API_PORT'))
            
            self.config = config
            return config
            
        except ConfigurationError as e:
            raise e
        except Exception as e:
            raise ConfigurationError(
                message=f"Failed to load configuration: {str(e)}",
                error_code="CONFIG_LOAD_FAILED"
            )
    
    def initialize_app_context(self) -> AppContext:
        """
        Initialize application context with logger and config.
        
        Returns:
            AppContext: Initialized application context
        """
        if self.logger is None:
            raise ConfigurationError(
                message="Logger not initialized. Call setup_logging() first.",
                error_code="LOGGER_NOT_INITIALIZED"
            )
        
        if self.config is None:
            raise ConfigurationError(
                message="Configuration not loaded. Call load_configuration() first.",
                error_code="CONFIG_NOT_LOADED"
            )
        
        # Use the global app context
        ctx.logger = self.logger
        ctx.config = self.config
        self.app_context = ctx
        
        return ctx
    
    def initialize_application(self) -> any:
        """
        Create and initialize the core application.
        
        Returns:
            Application instance
        """
        if self.config is None or self.logger is None:
            raise ConfigurationError(
                message="Bootstrap not fully initialized",
                error_code="BOOTSTRAP_INCOMPLETE"
            )
        
        self.logger.info("Initializing application factory")
        app = ApplicationFactory.create(self.config)
        ApplicationFactory.set_instance(app)
        app.initialize()
        
        self.app = app
        self.logger.info("Application initialized successfully")
        return app
    
    def bootstrap(self, debug: bool = False) -> "Bootstrap":
        """
        Run complete bootstrap process.
        
        Args:
            debug: Enable debug mode
            
        Returns:
            Bootstrap: Self for chaining
            
        Raises:
            ConfigurationError: If any step fails
        """
        if self._initialized:
            self.logger.debug("Bootstrap already initialized, skipping")
            return self
        
        try:
            # Step 1: Load environment
            self.load_environment()
            
            # Step 2: Setup logging
            self.setup_logging(debug=debug)
            self.logger.info("PyArgus bootstrapping started")
            
            # Step 3: Load configuration
            self.load_configuration()
            self.logger.debug(f"Configuration loaded: env={self.config.environment}")
            
            # Step 4: Initialize app context
            self.initialize_app_context()
            self.logger.debug("App context initialized")
            
            # Step 5: Initialize application
            self.initialize_application()
            
            self._initialized = True
            self.logger.info("PyArgus bootstrap completed successfully")
            
            return self
            
        except ConfigurationError as e:
            error_msg = f"Bootstrap configuration error: {e.message}"
            if self.logger:
                self.logger.error(error_msg)
            print(f"\n❌ {error_msg}", file=sys.stderr)
            raise
        except Exception as e:
            error_msg = f"Bootstrap failed: {str(e)}"
            if self.logger:
                self.logger.error(error_msg, exc_info=True)
            print(f"\n❌ {error_msg}", file=sys.stderr)
            raise ConfigurationError(
                message=error_msg,
                error_code="BOOTSTRAP_FAILED"
            )
    
    @property
    def is_initialized(self) -> bool:
        """Check if bootstrap has been completed."""
        return self._initialized
