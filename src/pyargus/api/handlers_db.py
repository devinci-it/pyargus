"""
Database-backed API handlers for PyArgus.

This module replaces in-memory storage with Peewee ORM database persistence.
"""

from typing import Dict, Any, Tuple, Optional
import logging
from datetime import datetime
import hashlib

from pyargus.core.models import Client, SSHKey, TunnelAssignment, ServiceStatus
from pyargus.core.exceptions import ResourceConflictError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class PortManager:
    """Manages port allocation for SSH tunnels with database persistence."""
    
    PORT_START = 9221
    PORT_MAX = 9999
    
    @classmethod
    def get_next_available_port(cls) -> int:
        """
        Get the next available port for SSH tunnel assignment.
        
        Returns:
            Available port number
            
        Raises:
            Exception: If no ports are available
        """
        # Find all used ports
        used_ports = set()
        for assignment in TunnelAssignment.select().where(TunnelAssignment.is_active == True):
            used_ports.add(assignment.assigned_port)
        
        # Find next available
        for port in range(cls.PORT_START, cls.PORT_MAX + 1):
            if port not in used_ports:
                return port
        
        raise Exception(f"No available ports between {cls.PORT_START} and {cls.PORT_MAX}")
    
    @classmethod
    def assign_port(cls, client_id: str) -> int:
        """
        Assign a port to a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            Assigned port number
        """
        # Check if client already has an assignment
        existing = TunnelAssignment.select().where(
            TunnelAssignment.client_id == client_id
        ).first()
        
        if existing:
            return existing.assigned_port
        
        # Get next available port
        port = cls.get_next_available_port()
        
        # Create assignment
        assignment = TunnelAssignment.create(
            client_id=client_id,
            assigned_port=port,
            is_active=False
        )
        
        logger.info(f"Port assigned: {client_id} → {port}")
        return port
    
    @classmethod
    def get_assigned_port(cls, client_id: str) -> Optional[int]:
        """Get the port assigned to a client."""
        assignment = TunnelAssignment.select().where(
            TunnelAssignment.client_id == client_id
        ).first()
        return assignment.assigned_port if assignment else None


def _generate_key_fingerprint(public_key: str) -> str:
    """Generate SHA256 fingerprint of public key."""
    return hashlib.sha256(public_key.encode()).hexdigest()


def handle_client_registration(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Handle client registration with database persistence.
    
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
        
        # Check if client already exists
        existing = Client.select().where(Client.hostname == hostname).first()
        if existing:
            logger.warning(f"Registration failed: duplicate hostname {hostname}")
            return {
                'status': 'error',
                'error_code': 'DUPLICATE_CLIENT',
                'message': f'Client with hostname {hostname} already exists'
            }, 409
        
        # Create client
        client = Client.create(
            hostname=hostname,
            ip_address=ip_address,
            status='registered'
        )
        
        # Create SSH key
        fingerprint = _generate_key_fingerprint(public_key)
        SSHKey.create(
            client=client,
            public_key=public_key,
            key_fingerprint=fingerprint,
            is_active=True
        )
        
        # Assign port
        assigned_port = PortManager.assign_port(client.client_id)
        
        logger.info(
            f"Registration successful | client_id={client.client_id} | hostname={hostname} | "
            f"assigned_port={assigned_port}"
        )
        
        return {
            'status': 'success',
            'client_id': client.client_id,
            'assigned_port': assigned_port,
            'message': 'Client registered successfully'
        }, 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Registration failed: {str(e)}'
        }, 500


def handle_authentication(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Handle client authentication with database lookup.
    
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
        client = Client.get_by_id(client_id)
        if not client:
            logger.warning(f"Authentication failed: client not found | client_id={client_id}")
            return {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }, 404
        
        # TODO: Verify signature against public key
        if not signature or len(signature) < 10:
            logger.warning(f"Authentication failed: invalid signature | client_id={client_id}")
            return {
                'status': 'error',
                'error_code': 'INVALID_SIGNATURE',
                'message': 'Invalid signature format'
            }, 401
        
        # Check timestamp is reasonable (not too old)
        current_time = datetime.utcnow().timestamp()
        if abs(current_time - timestamp) > 300:  # 5 minute tolerance
            logger.warning(
                f"Authentication failed: invalid timestamp | client_id={client_id} | "
                f"age={abs(current_time - timestamp)}s"
            )
            return {
                'status': 'error',
                'error_code': 'INVALID_TIMESTAMP',
                'message': 'Timestamp is too old or in the future'
            }, 401
        
        # Update last seen
        client.last_seen = datetime.utcnow()
        client.save()
        
        logger.info(
            f"Authentication successful | client_id={client_id} | hostname={client.hostname} | "
            f"ip_address={client.ip_address}"
        )
        
        return {
            'status': 'success',
            'authenticated': True,
            'client_id': client_id,
            'message': 'Client authenticated successfully'
        }, 200
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Authentication failed: {str(e)}'
        }, 500


def handle_service_pre_config(client_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Handle service pre-configuration with database lookup.
    
    Args:
        client_id: The client ID
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug(f"Service pre-config requested | client_id={client_id}")
        
        # Get client
        client = Client.get_by_id(client_id)
        if not client:
            logger.warning(f"Service pre-config failed: client not found | client_id={client_id}")
            return {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }, 404
        
        # Get or assign port
        assignment = TunnelAssignment.select().where(
            TunnelAssignment.client_id == client_id
        ).first()
        
        if not assignment:
            assigned_port = PortManager.assign_port(client_id)
            logger.info(f"Port assigned during pre-config | client_id={client_id} | port={assigned_port}")
        else:
            assigned_port = assignment.assigned_port
        
        logger.info(f"Service pre-config successful | client_id={client_id} | port={assigned_port}")
        
        return {
            'status': 'success',
            'client_id': client_id,
            'assigned_port': assigned_port,
            'hostname': client.hostname,
            'ip_address': client.ip_address,
            'message': 'Service pre-configuration successful'
        }, 200
        
    except Exception as e:
        logger.error(f"Service pre-config error | client_id={client_id}: {str(e)}")
        return {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Pre-configuration failed: {str(e)}'
        }, 500


def handle_service_install(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Handle service installation/generation with database lookup.
    
    Args:
        request_data: Validated request data with client_id
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        client_id = request_data['client_id']
        logger.debug(f"Service install requested | client_id={client_id}")
        
        # Get client
        client = Client.get_by_id(client_id)
        if not client:
            logger.warning(f"Service install failed: client not found | client_id={client_id}")
            return {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }, 404
        
        # Get assignment
        assignment = TunnelAssignment.select().where(
            TunnelAssignment.client_id == client_id
        ).first()
        
        if not assignment:
            logger.error(f"Service install failed: no port assigned | client_id={client_id}")
            return {
                'status': 'error',
                'error_code': 'PORT_NOT_ASSIGNED',
                'message': 'Client has no assigned port'
            }, 400
        
        # Generate service file
        service_content = _generate_service_file(client_id, assignment.assigned_port, client.hostname)
        
        logger.info(
            f"Service file generated | client_id={client_id} | hostname={client.hostname} | "
            f"port={assignment.assigned_port}"
        )
        
        return {
            'status': 'success',
            'service_file_content': service_content,
            'assigned_port': assignment.assigned_port,
            'message': 'Service file generated successfully'
        }, 200
        
    except Exception as e:
        logger.error(f"Service install error: {str(e)}")
        return {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Service generation failed: {str(e)}'
        }, 500


def handle_service_status(client_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Handle service status check with database lookup.
    
    Args:
        client_id: The client ID
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug(f"Service status check | client_id={client_id}")
        
        # Get client
        client = Client.get_by_id(client_id)
        if not client:
            logger.warning(f"Status check failed: client not found | client_id={client_id}")
            return {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }, 404
        
        # Get latest status
        status_record = ServiceStatus.select().where(
            ServiceStatus.client_id == client_id
        ).order_by(ServiceStatus.update_timestamp.desc()).first()
        
        tunnel_active = False
        tunnel_status = 'inactive'
        
        if status_record:
            tunnel_status = status_record.tunnel_status
            tunnel_active = status_record.tunnel_status == 'active'
        
        # Get assignment
        assignment = TunnelAssignment.select().where(
            TunnelAssignment.client_id == client_id
        ).first()
        
        assigned_port = assignment.assigned_port if assignment else None
        
        logger.debug(
            f"Status checked | client_id={client_id} | hostname={client.hostname} | "
            f"tunnel={tunnel_status}"
        )
        
        return {
            'status': tunnel_status,
            'client_id': client_id,
            'assigned_port': assigned_port,
            'tunnel_active': tunnel_active,
            'message': f'Tunnel status is {tunnel_status}'
        }, 200
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Status check failed: {str(e)}'
        }, 500


def handle_health_check() -> Tuple[Dict[str, Any], int]:
    """
    Handle health check requests.
    
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug("Health check requested")
        
        return {
            'status': 'healthy',
            'version': '0.1.0',
            'message': 'PyArgus API is running',
            'services': {
                'database': 'connected',
                'ssh_manager': 'ready',
                'security': 'ready'
            }
        }, 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Health check failed: {str(e)}'
        }, 500


def handle_list_clients() -> Tuple[Dict[str, Any], int]:
    """
    Handle listing all clients from database.
    
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug("List clients requested")
        
        clients = []
        for client in Client.select():
            # Get tunnel assignment info
            assignment = TunnelAssignment.select().where(
                TunnelAssignment.client_id == client.client_id
            ).first()
            
            clients.append({
                'client_id': client.client_id,
                'hostname': client.hostname,
                'ip_address': client.ip_address,
                'status': client.status,
                'assigned_port': assignment.assigned_port if assignment else None,
                'created_at': client.created_at.isoformat(),
                'last_seen': client.last_seen.isoformat(),
            })
        
        logger.info(f"List clients operation | total_clients={len(clients)}")
        
        return {
            'status': 'success',
            'clients': clients,
            'total': len(clients),
            'message': 'Clients retrieved successfully'
        }, 200
        
    except Exception as e:
        logger.error(f"List clients error: {str(e)}")
        return {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Failed to retrieve clients: {str(e)}'
        }, 500


def handle_get_client(client_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Handle getting a specific client from database.
    
    Args:
        client_id: The client ID
        
    Returns:
        Tuple of (response_data, http_status_code)
    """
    try:
        logger.debug(f"Get client requested | client_id={client_id}")
        
        client = Client.get_by_id(client_id)
        if not client:
            logger.warning(f"Get client failed: not found | client_id={client_id}")
            return {
                'status': 'error',
                'error_code': 'CLIENT_NOT_FOUND',
                'message': f'Client {client_id} not found'
            }, 404
        
        # Get SSH keys
        keys = []
        for key in SSHKey.select().where(SSHKey.client_id == client_id):
            keys.append({
                'key_id': key.key_id,
                'key_type': key.key_type,
                'key_fingerprint': key.key_fingerprint,
                'is_active': key.is_active,
                'created_at': key.created_at.isoformat(),
                'last_used': key.last_used.isoformat() if key.last_used else None,
            })
        
        # Get tunnel assignment
        assignment = TunnelAssignment.select().where(
            TunnelAssignment.client_id == client_id
        ).first()
        
        return {
            'status': 'success',
            'client': {
                'client_id': client.client_id,
                'hostname': client.hostname,
                'ip_address': client.ip_address,
                'status': client.status,
                'assigned_port': assignment.assigned_port if assignment else None,
                'created_at': client.created_at.isoformat(),
                'last_seen': client.last_seen.isoformat(),
                'ssh_keys': keys,
            },
            'message': 'Client details retrieved successfully'
        }, 200
        
    except Exception as e:
        logger.error(f"Get client error: {str(e)}")
        return {
            'status': 'error',
            'error_code': 'SERVER_ERROR',
            'message': f'Failed to retrieve client: {str(e)}'
        }, 500


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
