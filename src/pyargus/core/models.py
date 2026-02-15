"""
Peewee ORM models for PyArgus database.

Defines the schema for:
- Client registrations
- SSH keys
- SSH tunnel assignments
- Service/tunnel status
"""

import uuid
from datetime import datetime
from peewee import (
    CharField, IntegerField, BooleanField, DateTimeField, 
    TextField, ForeignKeyField, Model
)
from pyargus.core.database import BaseModel


class Client(BaseModel):
    """
    Client registration model.
    
    Stores information about registered SSH bastion clients.
    """
    client_id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    hostname = CharField(unique=True, index=True)
    ip_address = CharField(index=True)
    status = CharField(default='registered', choices=['registered', 'active', 'inactive', 'suspended'])
    created_at = DateTimeField(default=datetime.utcnow)
    last_seen = DateTimeField(default=datetime.utcnow)
    
    class Meta:
        table_name = 'clients'
    
    def __repr__(self):
        return f"<Client {self.client_id}: {self.hostname}>"


class SSHKey(BaseModel):
    """
    SSH public key storage model.
    
    Stores SSH keys associated with clients for authentication.
    """
    key_id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    client = ForeignKeyField(Client, backref='ssh_keys', on_delete='CASCADE')
    public_key = TextField()
    key_type = CharField(default='rsa')  # rsa, ecdsa, ed25519, etc.
    key_fingerprint = CharField(unique=True, index=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    last_used = DateTimeField(null=True)
    
    class Meta:
        table_name = 'ssh_keys'
    
    def __repr__(self):
        return f"<SSHKey {self.key_id}: {self.key_type}>"


class TunnelAssignment(BaseModel):
    """
    SSH tunnel port assignment model.
    
    Tracks the mapping between clients and assigned remote ports.
    """
    assignment_id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    client = ForeignKeyField(Client, backref='tunnel_assignments', on_delete='CASCADE')
    assigned_port = IntegerField(unique=True, index=True)
    is_active = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    activated_at = DateTimeField(null=True)
    deactivated_at = DateTimeField(null=True)
    
    class Meta:
        table_name = 'tunnel_assignments'
    
    def __repr__(self):
        return f"<TunnelAssignment {self.assigned_port} → {self.client.hostname}>"


class ServiceStatus(BaseModel):
    """
    Service/tunnel status tracking model.
    
    Stores the current health and status of tunnel services.
    """
    status_id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    client = ForeignKeyField(Client, backref='status_history', on_delete='CASCADE')
    tunnel_status = CharField(default='inactive', choices=['inactive', 'connecting', 'active', 'error'])
    error_message = CharField(null=True)
    last_check = DateTimeField(default=datetime.utcnow)
    update_timestamp = DateTimeField(default=datetime.utcnow)
    
    class Meta:
        table_name = 'service_status'
        indexes = (
            # Create index on client + last_check for efficient queries
            (('client', 'last_check'), False),
        )
    
    def __repr__(self):
        return f"<ServiceStatus {self.client_id}: {self.tunnel_status}>"
