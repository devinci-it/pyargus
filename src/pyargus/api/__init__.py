"""API module for PyArgus."""

from .schemas import (
    SchemaValidationError,
    ClientRegistrationRequest,
    ClientAuthRequest,
    ServiceInstallRequest,
    ClientRegistrationResponse,
    ServiceInstallResponse,
    ServicePreConfigResponse,
    ServiceStatusResponse,
    HealthCheckResponse,
    ErrorResponse,
)

from .handlers import (
    PortAllocationError,
    HandlerError,
    ClientAlreadyExistsError,
    ClientNotFoundError,
    InvalidAuthenticationError,
    PortManager,
    ClientRegistry,
    handle_client_registration,
    handle_authentication,
    handle_service_pre_config,
    handle_service_install,
    handle_service_status,
    handle_health_check,
    handle_list_clients,
)

from .routes import api_blueprint

__all__ = [
    # Schemas
    'SchemaValidationError',
    'ClientRegistrationRequest',
    'ClientAuthRequest',
    'ServiceInstallRequest',
    'ClientRegistrationResponse',
    'ServiceInstallResponse',
    'ServicePreConfigResponse',
    'ServiceStatusResponse',
    'HealthCheckResponse',
    'ErrorResponse',
    # Handlers
    'PortAllocationError',
    'HandlerError',
    'ClientAlreadyExistsError',
    'ClientNotFoundError',
    'InvalidAuthenticationError',
    'PortManager',
    'ClientRegistry',
    'handle_client_registration',
    'handle_authentication',
    'handle_service_pre_config',
    'handle_service_install',
    'handle_service_status',
    'handle_health_check',
    'handle_list_clients',
    # Routes
    'api_blueprint',
]
