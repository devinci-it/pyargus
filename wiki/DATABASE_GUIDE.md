# PyArgus Database Setup Guide

## Overview

PyArgus now has full database support using **Peewee ORM** with **SQLite** as the default backend. The database persists all client registrations, SSH keys, port assignments, and service status information.

## Database Architecture

### Tables

#### 1. **clients** - Client Registration Data
Stores all registered bastion clients.

| Column | Type | Description |
|--------|------|-------------|
| `client_id` | VARCHAR | Primary key, UUID |
| `hostname` | VARCHAR | Client hostname (unique) |
| `ip_address` | VARCHAR | Client's IP address |
| `status` | VARCHAR | Status: registered, active, inactive, suspended |
| `created_at` | DATETIME | Registration timestamp |
| `last_seen` | DATETIME | Last authentication timestamp |

**Indexes:**
- `client_id` (PK)
- `hostname` (UNIQUE)
- `ip_address`

#### 2. **ssh_keys** - SSH Public Keys
Stores SSH public keys associated with each client for authentication.

| Column | Type | Description |
|--------|------|-------------|
| `key_id` | VARCHAR | Primary key, UUID |
| `client_id` | VARCHAR | Foreign key to clients |
| `public_key` | TEXT | Full SSH public key |
| `key_type` | VARCHAR | Key type: rsa, ecdsa, ed25519 |
| `key_fingerprint` | VARCHAR | SHA256 fingerprint (unique) |
| `is_active` | BOOLEAN | Is this key active for auth? |
| `created_at` | DATETIME | Key creation timestamp |
| `last_used` | DATETIME | Last authentication attempt |

**Indexes:**
- `key_id` (PK)
- `client_id` (FK)
- `key_fingerprint` (UNIQUE)

#### 3. **tunnel_assignments** - Port Allocations
Tracks the mapping between clients and their assigned remote SSH ports (9221-9999).

| Column | Type | Description |
|--------|------|-------------|
| `assignment_id` | VARCHAR | Primary key, UUID |
| `client_id` | VARCHAR | Foreign key to clients |
| `assigned_port` | INT | Assigned remote port (9221-9999) |
| `is_active` | BOOLEAN | Is this assignment currently active? |
| `created_at` | DATETIME | Assignment timestamp |
| `activated_at` | DATETIME | When tunnel became active |
| `deactivated_at` | DATETIME | When tunnel was deactivated |

**Indexes:**
- `assignment_id` (PK)
- `client_id` (FK)
- `assigned_port` (UNIQUE)

#### 4. **service_status** - Tunnel Status Tracking
Stores the status history of SSH tunnel services.

| Column | Type | Description |
|--------|------|-------------|
| `status_id` | VARCHAR | Primary key, UUID |
| `client_id` | VARCHAR | Foreign key to clients |
| `tunnel_status` | VARCHAR | Status: inactive, connecting, active, error |
| `error_message` | VARCHAR | Error details if status is error |
| `last_check` | DATETIME | Timestamp of last status check |
| `update_timestamp` | DATETIME | Record update time |

**Indexes:**
- `status_id` (PK)
- `client_id`, `last_check` (composite index)

## Setup Instructions

### 1. Initialize the Database

Run the setup script to create all tables:

```bash
cd /home/davinci/Development/python/pyargus
pipenv run python setup_database.py
```

**Output:**
```
================================================================================
PyArgus Database Initialization
================================================================================
Initializing database connection...
✓ Database initialized at: pyargus.db
Creating tables...
✓ Tables created successfully

Database Tables:
  - Client (clients table)
  - SSHKey (ssh_keys table)
  - TunnelAssignment (tunnel_assignments table)
  - ServiceStatus (service_status table)

================================================================================
✓ Database initialization completed successfully
================================================================================
```

### 2. Verify Database Creation

```bash
# Check database file
ls -lh pyargus.db

# List tables
sqlite3 pyargus.db ".tables"

# View schema
sqlite3 pyargus.db ".schema"

# Count records
sqlite3 pyargus.db "SELECT COUNT(*) FROM clients;"
```

### 3. Reset Database (if needed)

To drop all tables and reinitialize:

```bash
pipenv run python setup_database.py --reset
```

### 4. Custom Database Path

To initialize database at a custom location:

```bash
pipenv run python setup_database.py --path /path/to/custom/pyargus.db
```

### 5. Environment Configuration

Database path can be overridden via environment variable:

```bash
export DATABASE_URL="sqlite:///path/to/pyargus.db"
```

Or in `.env`:

```env
DATABASE_URL=sqlite:///path/to/pyargus.db
DATABASE_ECHO=false  # Set to true for SQL logging
```

## Database-Backed API Handlers

The handlers have been rewritten to use the database instead of in-memory storage:

### File Location
`src/pyargus/api/handlers_db.py`

### Integrated Classes

#### PortManager (Database-Backed)
```python
from pyargus.api.handlers_db import PortManager

# Get next available port from database
port = PortManager.get_next_available_port()

# Assign port to client (saves to DB)
assigned_port = PortManager.assign_port(client_id)

# Get assigned port
port = PortManager.get_assigned_port(client_id)
```

### Handler Functions (Database-Backed)
```python
from pyargus.api.handlers_db import (
    handle_client_registration,
    handle_authentication,
    handle_service_pre_config,
    handle_service_install,
    handle_service_status,
    handle_health_check,
    handle_list_clients,
    handle_get_client
)

# All handlers now use database for persistence
response, status_code = handle_client_registration(request_data)
```

## Integration With API

### Switching to Database-Backed Handlers

To use the database-backed handlers instead of in-memory storage:

1. **Update routes.py** to import from `handlers_db`:
   ```python
   from pyargus.api.handlers_db import (
       handle_client_registration,
       handle_authentication,
       # ... other handlers
   )
   ```

2. **Initialize database** when Flask app starts:
   ```python
   from pyargus.core import init_database, create_tables
   
   def create_app():
       app = Flask(__name__)
       init_database()
       create_tables()
       # ... rest of setup
       return app
   ```

3. **Test with database**:
   ```bash
   pipenv run python run_server.py --debug
   ```

## Data Persistence

Unlike the in-memory storage (which was lost on server restart), database-backed handlers persist data:

| Feature | In-Memory | Database |
|---------|-----------|----------|
| **Data Persistence** | Lost on restart | Persistent |
| **Concurrent Access** | Limited | Full support |
| **Query Capability** | Dictionary iteration | Full SQL queries |
| **Scalability** | Limited to RAM | Unlimited (within disk) |
| **Backup** | Not possible | Full database backups |

## Example Workflow

### 1. Register Client (Saves to DB)
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "production-box-01",
    "ip_address": "203.0.113.45",
    "public_key": "ssh-rsa AAAA..."
  }'
```

**Response:**
```json
{
  "status": "success",
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "assigned_port": 9221,
  "message": "Client registered successfully"
}
```

**Database Result:**
- ✓ Row inserted in `clients` table
- ✓ Row inserted in `ssh_keys` table
- ✓ Row inserted in `tunnel_assignments` table
- ✓ All data persists after server restart

### 2. Restart Server (Data Still There)
```bash
# Server restarts
pipenv run python run_server.py

# Client data is still in database
curl http://localhost:5000/api/clients
```

**Response:**
```json
{
  "status": "success",
  "clients": [
    {
      "client_id": "123e4567-e89b-12d3-a456-426614174000",
      "hostname": "production-box-01",
      "ip_address": "203.0.113.45",
      "assigned_port": 9221,
      "status": "registered",
      "created_at": "2026-02-14T22:16:00...",
      "last_seen": "2026-02-14T22:16:00..."
    }
  ],
  "total": 1
}
```

## Database Querying

### Direct Database Queries

```python
from pyargus.core import Client, SSHKey, TunnelAssignment, ServiceStatus

# Get all clients
all_clients = Client.select()

# Get client by hostname
client = Client.get(Client.hostname == "production-box-01")

# Get client's SSH keys
for key in SSHKey.select().where(SSHKey.client_id == client.client_id):
    print(f"Key: {key.key_fingerprint}")

# Get all active tunnel assignments
active_ports = TunnelAssignment.select().where(
    TunnelAssignment.is_active == True
)

# Count total registrations
count = Client.select().count()
```

### Using SQLite CLI

```bash
# Connect to database
sqlite3 pyargus.db

# List all clients
SELECT client_id, hostname, ip_address, status FROM clients;

# Find client by hostname
SELECT * FROM clients WHERE hostname = 'production-box-01';

# Get assigned ports
SELECT c.hostname, ta.assigned_port 
FROM tunnel_assignments ta 
JOIN clients c ON ta.client_id = c.client_id;

# Check service status
SELECT c.hostname, ss.tunnel_status, ss.last_check 
FROM service_status ss 
JOIN clients c ON ss.client_id = c.client_id 
ORDER BY ss.update_timestamp DESC;
```

## Migration Path

### Current Status
- ✓ Models defined
- ✓ Database initialized
- ✓ Handlers rewritten (handlers_db.py)
- ⏳ Routes need updating to use handlers_db.py

### Next Steps
1. Update `src/pyargus/api/routes.py` to import `handlers_db`
2. Update `run_server.py` to initialize database
3. Add database connection middleware
4. Run full test suite
5. Remove old handler functions (keep as backup initially)

## Troubleshooting

### Database Connection Error
```python
# Error: "No database found"
# Solution: Run setup_database.py first
pipenv run python setup_database.py
```

### "Table already exists" Error
```python
# Error during create_tables()
# Solution: Tables are created with safe=True, should be ignored
# If error persists, reset: python setup_database.py --reset
```

### Port All Allocated
```python
# Error: "No available ports"
# Solution: Ports 9221-9999 are tracked in tunnel_assignments
# Check: sqlite3 pyargus.db "SELECT COUNT(*) FROM tunnel_assignments;"
# Maximum 779 concurrent clients (9999 - 9221)
```

## References

- [Peewee ORM Documentation](http://docs.peewee-orm.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Database Models](src/pyargus/core/models.py)
- [Database Initialization](src/pyargus/core/database.py)
- [Database-Backed Handlers](src/pyargus/api/handlers_db.py)
