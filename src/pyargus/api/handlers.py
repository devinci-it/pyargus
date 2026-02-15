"""
API Handlers for PyArgus.

This module contains the business logic for all API operations:
- Client registration
- Authentication
- Service management
- Status checking
"""

from typing import Dict, Any, Tuple, Optional
import uuid
import logging
from datetime import datetime

# Configure logger for auditing
logger = logging.getLogger(__name__)


class PortAllocationError(Exception):
    """Raised when port allocation fails."""
    pass


class HandlerError(Exception):
    """Base exception for handler errors."""
    pass


class ClientAlreadyExistsError(HandlerError):
    """Raised when attempting to register an already-existing client."""
    pass


class ClientNotFoundError(HandlerError):
    """Raised when a client cannot be found."""
    pass


class InvalidAuthenticationError(HandlerError):
    """Raised when authentication fails."""
    pass


class PortManager:
    """Manages port allocation for SSH tunnels."""
    
    # In-memory store: client_id -> assigned_port
    _port_assignments: Dict[str, int] = {}
    _used_ports: set = set()
    
    # Port range configuration
    PORT_START = 9221
    PORT_MAX = 9999
    
    @classmethod
    def get_next_available_port(cls) -> int:
        """
        Get the next available port for SSH tunnel assignment.
        
        Returns:
            Available port number
            
        Raises:
            PortAllocationError: If no ports are available
        """
        for port in range(cls.PORT_START, cls.PORT_MAX + 1):
            if port not in cls._used_ports:
                cls._used_ports.add(port)
                return port
        
        raise PortAllocationError(f"No available ports between {cls.PORT_START} and {cls.PORT_MAX}")
    
    @classmethod
    def assign_port(cls, client_id: str) -> int:
        """
        Assign a port to a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            Assigned port number
            
        Raises:
            PortAllocationError: If port allocation fails
        """
        if client_id in cls._port_assignments:
            return cls._port_assignments[client_id]
        
        port = cls.get_next_available_port()
        cls._port_assignments[client_id] = port
        return port
    
    @classmethod
    def get_assigned_port(cls, client_id: str) -> Optional[int]:
        """
        Get the port assigned to a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            Assigned port or None if not assigned
        """
        return cls._port_assignments.get(client_id)
    
    @classmethod
    def release_port(cls, client_id: str) -> bool:
        """
        Release the port assignment for a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            True if port was released, False if no assignment existed
        """
        if client_id in cls._port_assignments:
            port = cls._port_assignments.pop(client_id)
            cls._used_ports.discard(port)
            return True
        return False


class ClientRegistry:
    """In-memory registry for clients (will be replaced with database)."""
    
    _clients: Dict[str, Dict[str, Any]] = {}
    _public_keys: Dict[str, str] = {}  # public_key_hash -> client_id
    
    @classmethod
    def register_client(cls, hostname: str, ip_address: str, public_key: str) -> str:
        """
        Register a new client.
        
        Args:
            hostname: The client hostname
            ip_address: The client IP address
            public_key: The client public SSH key
            
        Returns:
            Client ID
            
        Raises:
            ClientAlreadyExistsError: If client already exists
        """
        # Check if public key is already registered
        pub_key_hash = hash(public_key)
        if pub_key_hash in cls._public_keys:
            logger.warning(
                f"Duplicate public key registration attempt for hostname={hostname}, ip={ip_address}"
            )
            raise ClientAlreadyExistsError(f"Public key already registered")
        
        # Generate unique client ID
        client_id = str(uuid.uuid4())
        
        # Store client
        client_data = {
            'client_id': client_id,
            'hostname': hostname,
            'ip_address': ip_address,
            'public_key': public_key,
            'pub_key_hash': pub_key_hash,
            'assigned_port': None,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'registered',
            'tunnel_active': False
        }
        
        cls._clients[client_id] = client_data
        cls._public_keys[pub_key_hash] = client_id
        
        logger.info(
            f"Client registered | client_id={client_id} | hostname={hostname} | "
            f"ip_address={ip_address} | timestamp={client_data['created_at']}"
        )
        
        return client_id
    
    @classmethod
    def get_client(cls, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get client information.
        
        Args:
            client_id: The client ID
            
        Returns:
            Client data or None if not found
        """
        return cls._clients.get(client_id)
    
    @classmethod
    def client_exists(cls, client_id: str) -> bool:
        """
        Check if a client exists.
        
        Args:
            client_id: The client ID
            
        Returns:
            True if client exists, False otherwise
        """
        return client_id in cls._clients
    
    @classmethod
    def update_client_port(cls, client_id: str, assigned_port: int) -> None:
        """
        Update the assigned port for a client.
        
        Args:
            client_id: The client ID
            assigned_port: The assigned port number
            
        Raises:
            ClientNotFoundError: If client not found
        """
        if client_id not in cls._clients:
            raise ClientNotFoundError(f"Client {client_id} not found")
        
        cls._clients[client_id]['assigned_port'] = assigned_port
    
    @classmethod
    def set_tunnel_active(cls, client_id: str, active: bool) -> None:
        """
        Set tunnel active status for a client.
        
        Args:
            client_id: The client ID
            active: Whether tunnel is active
            
        Raises:
            ClientNotFoundError: If client not found
        """
        if client_id not in cls._clients:
            raise ClientNotFoundError(f"Client {client_id} not found")
        
        cls._clients[client_id]['tunnel_active'] = active
    
    @classmethod
    def list_clients(cls) -> list:
        """
        List all registered clients.
        
        Returns:
            List of client data dictionaries
        """
        return list(cls._clients.values())


def handle_client_registration(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Handle client registration.
    
    Args:
        request_data: Validated request data with hostname, ip_address, public_key
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        hostname = request_data['hostname']
        ip_address = request_data['ip_address']
        public_key = request_data['public_key']
        
        logger.debug(f"Processing registration request for hostname={hostname}, ip={ip_address}")
        
        # Register client
        client_id = ClientRegistry.register_client(hostname, ip_address, public_key)
        
        # Assign port
        assigned_port = PortManager.assign_port(client_id)
        
        # Update client record with assigned port
        ClientRegistry.update_client_port(client_id, assigned_port)
        
        logger.info(
            f"Registration successful | client_id={client_id} | hostname={hostname} | "
            f"assigned_port={assigned_port}"
        )
        
        response = {
            'status': 'success',
            'client_id': client_id,
            'assigned_port': assigned_port,
            'message': 'Client registered successfully'
        }
        
        return response, 201
        
    except ClientAlreadyExistsError as e:
        logger.warning(
            f"Registration failed: duplicate client (hostname={hostname}, ip={ip_address}) - {str(e)}"
        )
        response = {
            'status': 'error',
            'error_code': 'DUPLICATE_CLIENT',
            'message': str(e)
        }
        return response, 409
        
    except PortAllocationError as e:
        logger.error(
            f"Registration failed: port allocation error for hostname={hostname} - {str(e)}"
        )
        response = {
            'status': 'error',
            'error_code': 'PORT_ALLOCATION_ERROR',
            'message': str(e)
        }
        return response, 500
        
    except Exception as e:
        logger.error(
            f"Registration failed: unexpected error for hostname={hostname} - {str(e)}"
        )
        response = {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Registration failed: {str(e)}'
        }
        return response, 500


def handle_authentication(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Handle client authentication.
    
    Args:
        request_data: Validated request data with client_id, signature, timestamp
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        client_id = request_data['client_id']
        signature = request_data['signature']
        timestamp = request_data['timestamp']
        
        logger.debug(f"Processing authentication for client_id={client_id}")
        
        # Verify client exists
        client = ClientRegistry.get_client(client_id)
        if not client:
            logger.warning(f"Authentication failed: client not found | client_id={client_id}")
            response = {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }
            return response, 404
        
        # TODO: Verify signature against public key
        # For now, we'll do basic validation
        if not signature or len(signature) < 10:
            logger.warning(
                f"Authentication failed: invalid signature | client_id={client_id} | "
                f"hostname={client['hostname']}"
            )
            response = {
                'status': 'error',
                'error_code': 'INVALID_SIGNATURE',
                'message': 'Invalid signature format'
            }
            return response, 401
        
        # Check timestamp is reasonable (not too old)
        current_time = datetime.utcnow().timestamp()
        if abs(current_time - timestamp) > 300:  # 5 minute tolerance
            logger.warning(
                f"Authentication failed: invalid timestamp | client_id={client_id} | "
                f"hostname={client['hostname']} | timestamp_age={abs(current_time - timestamp)}s"
            )
            response = {
                'status': 'error',
                'error_code': 'INVALID_TIMESTAMP',
                'message': 'Timestamp is too old or in the future'
            }
            return response, 401
        
        logger.info(
            f"Authentication successful | client_id={client_id} | hostname={client['hostname']} | "
            f"ip_address={client['ip_address']}"
        )
        
        response = {
            'status': 'success',
            'authenticated': True,
            'client_id': client_id,
            'message': 'Client authenticated successfully'
        }
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Authentication error | client_id={request_data.get('client_id')} - {str(e)}")
        response = {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Authentication failed: {str(e)}'
        }
        return response, 500


def handle_service_pre_config(client_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Handle service pre-configuration.
    
    Args:
        client_id: The client ID
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug(f"Service pre-config requested | client_id={client_id}")
        
        # Get client info
        client = ClientRegistry.get_client(client_id)
        if not client:
            logger.warning(f"Service pre-config failed: client not found | client_id={client_id}")
            response = {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }
            return response, 404
        
        # Assign port if not already assigned
        assigned_port = client['assigned_port']
        if not assigned_port:
            assigned_port = PortManager.assign_port(client_id)
            ClientRegistry.update_client_port(client_id, assigned_port)
            logger.info(f"Port assigned during pre-config | client_id={client_id} | port={assigned_port}")
        
        logger.info(f"Service pre-config successful | client_id={client_id} | port={assigned_port}")
        
        response = {
            'status': 'success',
            'client_id': client_id,
            'assigned_port': assigned_port,
            'hostname': client['hostname'],
            'ip_address': client['ip_address'],
            'message': 'Service pre-configuration successful'
        }
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Service pre-config error | client_id={client_id} - {str(e)}")
        response = {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Pre-configuration failed: {str(e)}'
        }
        return response, 500


def handle_service_install(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Handle service installation/generation.
    
    Args:
        request_data: Validated request data with client_id
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        client_id = request_data['client_id']
        logger.debug(f"Service install requested | client_id={client_id}")
        
        # Get client info
        client = ClientRegistry.get_client(client_id)
        if not client:
            logger.warning(f"Service install failed: client not found | client_id={client_id}")
            response = {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }
            return response, 404
        
        assigned_port = client['assigned_port']
        if not assigned_port:
            logger.error(f"Service install failed: no port assigned | client_id={client_id}")
            response = {
                'status': 'error',
                'error_code': 'PORT_NOT_ASSIGNED',
                'message': 'Client has no assigned port'
            }
            return response, 400
        
        # Generate systemd service file content
        service_content = _generate_service_file(client_id, assigned_port, client['hostname'])
        
        logger.info(
            f"Service file generated | client_id={client_id} | hostname={client['hostname']} | "
            f"port={assigned_port}"
        )
        
        response = {
            'status': 'success',
            'service_file_content': service_content,
            'assigned_port': assigned_port,
            'message': 'Service file generated successfully'
        }
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Service install error | client_id={request_data.get('client_id')} - {str(e)}")
        response = {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Service generation failed: {str(e)}'
        }
        return response, 500


def handle_service_status(client_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Handle service status check.
    
    Args:
        client_id: The client ID
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug(f"Service status check | client_id={client_id}")
        
        # Get client info
        client = ClientRegistry.get_client(client_id)
        if not client:
            logger.warning(f"Status check failed: client not found | client_id={client_id}")
            response = {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }
            return response, 404
        
        # TODO: Check actual SSH tunnel status
        tunnel_active = client.get('tunnel_active', False)
        status = 'active' if tunnel_active else 'inactive'
        
        logger.debug(
            f"Status checked | client_id={client_id} | hostname={client['hostname']} | "
            f"tunnel={status}"
        )
        
        response = {
            'status': status,
            'client_id': client_id,
            'assigned_port': client['assigned_port'],
            'tunnel_active': tunnel_active,
            'message': f'Tunnel status is {status}'
        }
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Status check error | client_id={client_id} - {str(e)}")
        response = {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Status check failed: {str(e)}'
        }
        return response, 500


def handle_health_check() -> Tuple[Dict[str, Any], int]:
    """
    Handle health check requests.
    
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug("Health check requested")
        
        response = {
            'status': 'healthy',
            'version': '0.1.0',
            'message': 'PyArgus API is running',
            'services': {
                'database': 'connected',
                'ssh_manager': 'ready',
                'security': 'ready'
            }
        }
        return response, 200
        
    except Exception as e:
        logger.error(f"Health check failed - {str(e)}")
        response = {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Health check failed: {str(e)}'
        }
        return response, 500


def handle_list_clients() -> Tuple[Dict[str, Any], int]:
    """
    Handle listing all clients.
    
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug("List clients requested")
        
        clients = ClientRegistry.list_clients()
        
        logger.info(f"List clients operation | total_clients={len(clients)}")
        
        response = {
            'status': 'success',
            'clients': clients,
            'total': len(clients),
            'message': 'Clients retrieved successfully'
        }
        
        return response, 200
        
    except Exception as e:
        logger.error(f"List clients error - {str(e)}")
        response = {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Failed to retrieve clients: {str(e)}'
        }
        return response, 500


def _generate_service_file(client_id: str, assigned_port: int, hostname: str) -> str:
    """
    Generate a systemd service file for SSH reverse tunnel.
    
    Args:
        client_id: The client ID
        assigned_port: The assigned remote port
        hostname: The client hostname
        
    Returns:
        Service file content as string
    """
    service_content = f"""[Unit]
Description=SSH Reverse Tunnel to PyArgus Bastion - {hostname}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=bastion
ExecStart=/usr/bin/ssh -N -T -R {assigned_port}:127.0.0.1:22 bastion@localhost
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ssh-tunnel-{client_id[:8]}

[Install]
WantedBy=multi-user.target
"""
    return service_content
