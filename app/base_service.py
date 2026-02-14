"""
Base Service Classes for PyArgus.

Provides abstract base classes for implementing services following SOLID principles.
All application services (managers) should inherit from BaseService to ensure
consistent lifecycle management, logging, and error handling.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict

from .application import ILogger
from .exceptions import PyArgusException


class BaseService(ABC):
    """
    Abstract base class for all application services.
    
    Provides common functionality for service initialization, lifecycle management,
    logging, and error handling. Follows the Single Responsibility Principle by
    defining a clear interface that all services must implement.
    
    Example:
        class UserService(BaseService):
            def initialize(self) -> None:
                # Initialize service-specific resources
                pass
            
            def shutdown(self) -> None:
                # Cleanup service-specific resources
                pass
            
            def health_check(self) -> Dict[str, Any]:
                # Return health status
                return {"status": "healthy", "name": self.service_name}
    """
    
    def __init__(self, service_name: str, logger: ILogger):
        """
        Initialize base service.
        
        Args:
            service_name: Unique name for this service
            logger: ILogger instance for logging
        """
        self._service_name = service_name
        self._logger = logger
        self._is_initialized = False
        self._metadata: Dict[str, Any] = {}
    
    @property
    def service_name(self) -> str:
        """Get service name."""
        return self._service_name
    
    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized."""
        return self._is_initialized
    
    @property
    def logger(self) -> ILogger:
        """Get logger instance."""
        return self._logger
    
    def initialize(self) -> None:
        """
        Initialize service.
        
        Override this method in subclasses to perform service-specific initialization.
        Always call super().initialize() first.
        """
        self._logger.info(f"Initializing {self._service_name}...")
        self._is_initialized = True
        self._logger.info(f"{self._service_name} initialized successfully")
    
    def shutdown(self) -> None:
        """
        Gracefully shutdown service.
        
        Override this method in subclasses to perform service-specific cleanup.
        Always call super().shutdown() last.
        """
        self._logger.info(f"Shutting down {self._service_name}...")
        self._is_initialized = False
        self._logger.info(f"{self._service_name} shutdown completed")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform service health check.
        
        Override this method to implement service-specific health checks.
        Should return a dictionary with at minimum {"status": "healthy" or "unhealthy"}.
        
        Returns:
            Dict with health status information
        """
        return {
            "service": self._service_name,
            "status": "healthy" if self._is_initialized else "unhealthy",
            "initialized": self._is_initialized,
        }
    
    def _ensure_initialized(self) -> None:
        """
        Ensure service is initialized before operations.
        
        Raises:
            PyArgusException: If service is not initialized
        """
        if not self._is_initialized:
            raise PyArgusException(
                f"Service '{self._service_name}' is not initialized. "
                "Call initialize() before using service.",
                error_code="SERVICE_NOT_INITIALIZED"
            )
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Store metadata about the service."""
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Retrieve metadata about the service."""
        return self._metadata.get(key, default)


class ServiceRegistry:
    """
    Registry for managing multiple services.
    
    Implements the Registry pattern to centrally manage service lifecycle
    and provide access to multiple services.
    """
    
    def __init__(self, logger: ILogger):
        """
        Initialize service registry.
        
        Args:
            logger: ILogger instance
        """
        self._services: Dict[str, BaseService] = {}
        self._logger = logger
    
    def register(self, service: BaseService) -> None:
        """
        Register a service.
        
        Args:
            service: Service instance to register
            
        Raises:
            PyArgusException: If service with same name already exists
        """
        if service.service_name in self._services:
            raise PyArgusException(
                f"Service '{service.service_name}' already registered",
                error_code="SERVICE_CONFLICT"
            )
        
        self._services[service.service_name] = service
        self._logger.debug(f"Registered service: {service.service_name}")
    
    def get(self, service_name: str) -> BaseService:
        """
        Get registered service.
        
        Args:
            service_name: Name of service to retrieve
            
        Returns:
            BaseService instance
            
        Raises:
            PyArgusException: If service not found
        """
        if service_name not in self._services:
            raise PyArgusException(
                f"Service '{service_name}' not found",
                error_code="SERVICE_NOT_FOUND"
            )
        
        return self._services[service_name]
    
    def initialize_all(self) -> None:
        """Initialize all registered services."""
        self._logger.info("Initializing all services...")
        
        for service_name, service in self._services.items():
            try:
                service.initialize()
            except Exception as e:
                self._logger.error(
                    f"Failed to initialize service '{service_name}'",
                    e
                )
                raise
        
        self._logger.info(f"All {len(self._services)} services initialized")
    
    def shutdown_all(self) -> None:
        """Gracefully shutdown all registered services in reverse order."""
        self._logger.info("Shutting down all services...")
        
        # Shutdown in reverse order (LIFO)
        for service in reversed(list(self._services.values())):
            try:
                service.shutdown()
            except Exception as e:
                self._logger.error(
                    f"Error shutting down service '{service.service_name}'",
                    e
                )
        
        self._logger.info("All services shutdown completed")
    
    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health check on all services.
        
        Returns:
            Dict mapping service names to health check results
        """
        health_status = {}
        
        for service_name, service in self._services.items():
            try:
                health_status[service_name] = service.health_check()
            except Exception as e:
                health_status[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status
