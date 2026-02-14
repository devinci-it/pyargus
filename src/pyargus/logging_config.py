"""
PyArgus Logging Configuration Module.

Provides centralized logging configuration using PyLogger with decorators,
structured logging, and development/production mode support.
"""

from typing import Optional
from pylogger import (
    Logger as PyLogger,
    SettingsBuilder,
    build_log_decorator,
    SUCCESS_LEVEL,
    register_success_level
)

from .config import AppConfig


class LoggerConfigurator:
    """
    Centralized logging configuration using PyLogger.
    
    Handles:
    - PyLogger setup and configuration
    - Development vs production modes
    - Structured logging settings
    - Function call logging decorators
    """
    
    _configured = False
    _logger: Optional[PyLogger] = None
    _log_decorator = None
    
    @classmethod
    def configure(cls, config: AppConfig) -> PyLogger:
        """
        Configure PyLogger based on application config.
        
        Args:
            config: AppConfig instance with logging settings
            
        Returns:
            PyLogger: Configured logger instance
        """
        if cls._configured:
            return cls._logger
        
        logger = PyLogger.instance()
        
        # Configure based on environment
        is_dev = config.environment == "development"
        
        # Set development mode
        logger.set_development(is_dev)
        
        # Set level based on debug flag
        if config.debug:
            logger.setLevel(10)  # DEBUG
        else:
            level_map = {
                "DEBUG": 10,
                "INFO": 20,
                "WARNING": 30,
                "ERROR": 40,
                "CRITICAL": 50
            }
            logger.setLevel(level_map.get(config.log_level, 20))
        
        # Enable echo mode for development
        logger.set_echo(is_dev)
        
        # Register success level for custom logging
        try:
            register_success_level()
        except:
            pass  # Already registered
        
        cls._logger = logger
        cls._configured = True
        
        logger.info(
            f"PyArgus Logger configured",
            json_data={
                "environment": config.environment,
                "debug": config.debug,
                "level": config.log_level
            }
        )
        
        return logger
    
    @classmethod
    def get_logger(cls) -> PyLogger:
        """
        Get configured PyLogger instance.
        
        Returns:
            PyLogger: Singleton logger instance
        """
        if cls._logger is None:
            cls._logger = PyLogger.instance()
        return cls._logger
    
    @classmethod
    def get_decorator(cls, development: bool = False):
        """
        Get PyLogger decorator for function logging.
        
        Args:
            development: Whether to enable development mode for decorator
            
        Returns:
            Callable: Decorator for function/method logging
        """
        logger = cls.get_logger()
        return build_log_decorator(logger, development=development)
    
    @classmethod
    def reset(cls) -> None:
        """Reset logger configuration."""
        cls._configured = False
        cls._logger = None
        cls._log_decorator = None
