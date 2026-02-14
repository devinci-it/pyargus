# migrations/ - Database Migrations

Location: `/migrations/`

## Purpose

Contains database schema migrations for PyArgus. Manages database versioning and evolution as the application changes over time.

## Module Structure

```
migrations/
├── __init__.py                  # Package initialization
├── 001_initial_schema.py        # Initial database schema (Phase 1)
├── 002_client_extensions.py     # Future enhancements
└── ...
```

## Migration Strategy

### File Naming Convention
```
NNN_description.py

NNN = Three-digit version number (001, 002, 003, etc.)
description = Descriptive lowercase name
```

### Examples
- `001_initial_schema.py` - Initial tables
- `002_add_audit_logging.py` - Add audit tables
- `003_add_client_metadata.py` - Add metadata columns

## Planned Initial Schema (001_initial_schema.py)

```python
from peewee import *

"""
Initial database schema for PyArgus.

Tables:
- Client: Client information and configuration
- SSHKey: SSH keys for clients
- TunnelAssignment: Tunnel port assignments
- AuditLog: Audit trail for all operations
"""

class Client(Model):
    """Client registration and configuration."""
    id = CharField(primary_key=True)
    hostname = CharField(unique=True, index=True)
    ip_address = CharField()
    status = CharField(default="active")
    created_at = DateTimeField()
    updated_at = DateTimeField()
    
    class Meta:
        database = db
        table_name = "clients"

class SSHKey(Model):
    """SSH keys for clients."""
    id = AutoField()
    client = ForeignKeyField(Client, backref="ssh_keys")
    key_type = CharField()  # rsa, ed25519, ecdsa
    public_key_hash = CharField()
    private_key_encrypted = TextField()
    fingerprint = CharField(unique=True)
    created_at = DateTimeField()
    
    class Meta:
        database = db
        table_name = "ssh_keys"

class TunnelAssignment(Model):
    """Assigned tunnel ports for clients."""
    id = AutoField()
    client = ForeignKeyField(Client, backref="tunnel_assignments")
    assigned_port = IntegerField(unique=True)
    remote_host = CharField()
    status = CharField(default="active")
    created_at = DateTimeField()
    
    class Meta:
        database = db
        table_name = "tunnel_assignments"

class AuditLog(Model):
    """Audit trail for all operations."""
    id = AutoField()
    action = CharField()
    resource_type = CharField()
    resource_id = CharField()
    user_id = CharField(null=True)
    details = TextField()
    status = CharField()
    created_at = DateTimeField()
    
    class Meta:
        database = db
        table_name = "audit_logs"
```

## Migration Runner

```python
# migrations/runner.py

def run_migrations(database_url: str):
    """
    Execute all pending migrations.
    
    Args:
        database_url: Database connection string
    """
    db = Database(database_url)
    
    migrations = [
        "001_initial_schema",
        "002_additional_changes",
        # ...
    ]
    
    for migration in migrations:
        if not is_applied(migration):
            run_migration(migration, db)
            mark_applied(migration)
            logger.info(f"Applied migration: {migration}")

def rollback_migration(migration_name: str):
    """Rollback a specific migration."""
    pass

def get_migration_status() -> List[Dict]:
    """Get status of all migrations."""
    pass
```

## Usage

### Running Migrations

On application startup:

```python
# In Application.initialize()
from migrations.runner import run_migrations
from pyargus.config import config

run_migrations(config.database.database_url)
```

### Manual Migration

```bash
python -c "from migrations.runner import run_migrations; run_migrations('sqlite:///pyargus.db')"
```

## Migration Best Practices

### 1. One Change Per Migration
Each migration should make one logical change.

```python
# Good: Separate migrations
001_create_clients_table.py
002_add_audit_logging.py

# Bad: Multiple changes in one
001_create_tables_and_add_logging.py
```

### 2. Reversible Migrations
Each migration should be reversible.

```python
def forward(db):
    """Apply migration."""
    db.create_table(Client)

def backward(db):
    """Undo migration."""
    db.drop_table(Client)
```

### 3. Clear Naming
Use descriptive names that indicate what changes.

```python
# Good
002_add_client_metadata_fields.py

# Bad
002_updates.py
```

### 4. Idempotent Operations
Migrations should be safe to run multiple times.

```python
# Good: Check before creating
if not db.table_exists("clients"):
    db.create_table(Client)

# Bad: Assume table doesn't exist
db.create_table(Client)  # Fails if table exists
```

### 5. Data Migrations
Handle data migrations carefully.

```python
def data_migration(db):
    """Migrate existing data to new schema."""
    for client in Client.select():
        # Transform data
        client.new_field = transform(client.old_field)
        client.save()
```

## Database Schema Evolution

### Example: Adding New Feature

```python
# Original schema (001_initial_schema.py)
class Client(Model):
    id = CharField(primary_key=True)
    hostname = CharField()

# Feature request: Track client regions

# New migration (003_add_client_regions.py)
class AddClientRegion:
    def forward(db):
        # Add new column
        db.execute_sql(
            "ALTER TABLE clients ADD COLUMN region VARCHAR DEFAULT 'us-east-1'"
        )
    
    def backward(db):
        # Remove column
        db.execute_sql("ALTER TABLE clients DROP COLUMN region")
```

## Documentation

For each migration, include docstring:

```python
"""
Migration 002: Add Audit Logging

Purpose:
    Track all operations for security and debugging

Changes:
    - Create AuditLog table
    - Add audit_log_id foreign key to clients

Rollback:
    Drop AuditLog table

Dependencies:
    Requires 001_initial_schema.py
"""
```

## Testing Migrations

```python
import pytest
from migrations import runner

@pytest.mark.migration
def test_001_initial_schema_applies():
    """Test initial schema migration."""
    db = Database(":memory:")
    runner.apply_migration("001_initial_schema", db)
    
    # Verify tables exist
    assert db.table_exists("clients")
    assert db.table_exists("ssh_keys")
    assert db.table_exists("tunnel_assignments")

@pytest.mark.migration
def test_migration_data_integrity():
    """Test data is preserved across migrations."""
    # Create initial data
    # Apply migration
    # Verify data still exists
    pass
```

## Migration Checklist

Before committing a migration:

- [ ] Migration name follows convention (NNN_description.py)
- [ ] Migration is idempotent
- [ ] Migration can be reversed
- [ ] Tests pass
- [ ] Documentation is clear
- [ ] No breaking changes to API
- [ ] Performance considered
- [ ] Backward compatibility maintained

## Status: Phase 1 Initial Setup

Initial schema will be implemented in Phase 1. Additional migrations added as needed in later phases.

## See Also

- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md#phase-1-core-functionality)
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Database design
