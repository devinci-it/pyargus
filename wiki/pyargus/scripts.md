# scripts/ - Deployment & Setup Scripts

Location: `/scripts/`

## Purpose

Contains standalone scripts for deployment, setup, and operational tasks. Includes shell scripts and Python scripts for system-level operations.

## Module Structure

```
scripts/
├── __init__.py              # Package initialization
├── start_server.py          # Start API server (implemented)
├── setup.sh                 # Environment setup (Phase 1)
├── deploy_server.sh         # Server deployment (Phase 7)
├── deploy_client.sh         # Client installation (Phase 7)
├── cleanup.sh               # Cleanup operations (Phase 7)
└── docker/
    ├── Dockerfile           # Docker image
    └── docker-compose.yml   # Docker Compose config
```

## Implemented Scripts

### start_server.py
Start the PyArgus API server.

**Location**: `/scripts/start_server.py`

**Features**:
- Parse command-line arguments
- Load configuration
- Initialize application
- Start Uvicorn server
- Handle graceful shutdown

**Usage**:
```bash
python scripts/start_server.py
python scripts/start_server.py --host 0.0.0.0 --port 9000
python scripts/start_server.py --debug
python scripts/start_server.py --workers 8
```

**Example**:
```python
#!/usr/bin/env python3
import uvicorn
from pyargus import ApplicationFactory

# Create and initialize app
app = ApplicationFactory.create()

# Start server
uvicorn.run(
    "app.api:app",
    host=app.config.api.host,
    port=app.config.api.port,
    reload=app.config.api.reload,
    workers=app.config.api.workers,
    log_level=app.config.log_level.lower()
)
```

## Planned Scripts

### setup.sh
Initial environment setup.

**Purpose**:
- Install system dependencies
- Create directories
- Setup SSH keys
- Initialize database
- Configure permissions

**Usage**:
```bash
./scripts/setup.sh
./scripts/setup.sh --environment production
```

**Tasks**:
```bash
#!/bin/bash
set -e

echo "Setting up PyArgus..."

# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p /etc/pyargus
mkdir -p /var/log/pyargus
mkdir -p ~/.ssh

# Copy configuration
cp .env.example /etc/pyargus/.env

# Initialize database
python -m migrations.runner

# Setup permissions
chmod 700 /etc/pyargus
chmod 600 /etc/pyargus/.env

echo "Setup complete!"
```

### deploy_server.sh
Deploy server to production.

**Purpose**:
- Pull latest code
- Install dependencies
- Run migrations
- Start/restart services
- Backup existing data

**Usage**:
```bash
./scripts/deploy_server.sh
./scripts/deploy_server.sh --backup
./scripts/deploy_server.sh --rollback
```

**Tasks**:
```bash
#!/bin/bash
set -e

echo "Deploying PyArgus server..."

# Backup database
if [ "$BACKUP" = true ]; then
    cp pyargus.db pyargus.db.backup-$(date +%s)
fi

# Pull latest
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
python -m migrations.runner

# Restart service
systemctl restart pyargus

echo "Deployment complete!"
```

### deploy_client.sh
Deploy client-side systemd service.

**Purpose**:
- Download configuration
- Install SSH config
- Install systemd service
- Enable service
- Start tunnel

**Usage**:
```bash
./scripts/deploy_client.sh --server https://bastion.example.com --client-id c123456
```

**Tasks**:
```bash
#!/bin/bash

echo "Setting up SSH tunnel client..."

SERVER=$1
CLIENT_ID=$2

# Download service file
curl -o /tmp/ssh-az-bastion.service https://$SERVER/service/systemd/$CLIENT_ID

# Install service
sudo cp /tmp/ssh-az-bastion.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable ssh-az-bastion.service
sudo systemctl start ssh-az-bastion.service

echo "Client setup complete!"
```

### cleanup.sh
Cleanup and maintenance operations.

**Purpose**:
- Remove old services
- Archive logs
- Clean databases
- Remove temporary files

**Usage**:
```bash
./scripts/cleanup.sh
./scripts/cleanup.sh --archive-logs
./scripts/cleanup.sh --remove-inactive-clients
```

**Tasks**:
```bash
#!/bin/bash

echo "Running cleanup..."

# Archive old logs
find /var/log/pyargus -name "*.log" -mtime +30 -exec gzip {} \;

# Remove inactive clients
python -c "from pyargus.models import Client; \
    Client.delete().where(Client.status == 'inactive').execute()"

# Clean temp files
rm -rf /tmp/pyargus/*

echo "Cleanup complete!"
```

## Docker Scripts

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start server
CMD ["python", "main.py"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://pyargus:password@db:5432/pyargus
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - SSH_KEY_PATH=/app/ssh_keys/id_rsa
    volumes:
      - ./ssh_keys:/app/ssh_keys
      - ./logs:/app/logs
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: pyargus
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: pyargus
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## Script Development Best Practices

### 1. Error Handling
```bash
#!/bin/bash
set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure
```

### 2. Logging
```bash
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting deployment..."
log "ERROR: Something failed"
```

### 3. User Confirmation
```bash
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi
```

### 4. Help Text
```bash
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help      Show this help
    -d, --debug     Debug mode
    -v, --verbose   Verbose output
EOF
}
```

### 5. Argument Parsing
```bash
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--debug)
            DEBUG=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done
```

## Status: Phases 1 & 7

`start_server.py` implemented in Phase 1 (in main.py).
Deployment scripts planned for Phase 7 (Deployment & Containerization).

## See Also

- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Architecture overview
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md) - Development guide
