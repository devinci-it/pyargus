# PyArgus Implementation Plan - Step by Step

## Phase 1: Project Setup & Core Infrastructure (Week 1)

### Step 1: Initialize Project Structure
- [ ] Create directory structure matching the proposed layout
  - `app/`, `app/api/`, `app/security/`, `app/utils/`
  - `migrations/`, `scripts/`, `tests/`
- [ ] Create `__init__.py` files in all package directories
- [ ] Create `requirements.txt` with all dependencies:
  - `fastapi`, `uvicorn`
  - `peewee`, `sqlite3` (or PostgreSQL driver)
  - `paramiko` (SSH library)
  - `pycryptodome` (encryption)
  - `pydantic` (schemas)
  - `python-dotenv` (environment variables)
  - `pytest`, `pytest-cov` (testing)

### Step 2: Setup Configuration & Environment
- [ ] Create `.env.example` file with template variables
- [ ] Implement `app/config.py`:
  - Database connection string
  - Encryption key management
  - SSH configuration (ports, host)
  - API settings (host, port, debug mode)
- [ ] Create `.env` file for local development

### Step 3: Database Models (Peewee ORM)
- [ ] Create `app/models.py` with:
  - `Client` model (id, hostname, ip_address, created_at, updated_at)
  - `SSHKey` model (client_fk, public_key_hash, private_key_encrypted, key_type)
  - `TunnelAssignment` model (client_fk, assigned_port, local_port, status)
  - Add model relationships and validation
- [ ] Create initial migration: `migrations/001_initial_schema.py`
- [ ] Test database connection and table creation

---

## Phase 2: Security & Encryption Layer (Week 1-2)

### Step 4: Implement Encryption Module
- [ ] Create `app/security/encryption.py`:
  - `encrypt_key(private_key_content, encryption_key)` function
  - `decrypt_key(encrypted_key, encryption_key)` function
  - Use AES-256 with CBC mode
  - Generate secure IVs for each encryption
- [ ] Create `app/security/key_validator.py`:
  - `validate_public_key(public_key_string)` function
  - `validate_key_format(key_data)` function
  - Test for SSH RSA/ED25519 key formats

### Step 5: SSH Manager Implementation
- [ ] Create `app/ssh_manager.py`:
  - `load_ssh_key(key_path)` - load SSH key from file
  - `add_public_key_to_authorized_keys(public_key, client_id, port)` - add key with restrictions
  - `remove_public_key_from_authorized_keys(client_id)` - cleanup
  - `generate_restricted_command(client_id, assigned_port)` - create restricted SSH command
  - `verify_ssh_connection(client_info)` - test connectivity
  - Use Paramiko for SSH operations

### Step 6: Service Manager Implementation
- [ ] Create `app/service_manager.py`:
  - `generate_systemd_service_template(client_info, assigned_port)` - create service file content
  - `validate_service_config(service_content)` - verify service file syntax
  - `export_service_file(client_id, output_path)` - write service to file
  - Include ExecStart, Restart, RestartSec configurations

---

## Phase 3: REST API Implementation (Week 2-3)

### Step 7: API Schemas
- [ ] Create `app/api/schemas.py`:
  - `ClientRegistrationRequest` (hostname, ip_address, public_key)
  - `ClientAuthRequest` (client_id, signature, timestamp)
  - `ServiceInstallResponse` (service_file_content, assigned_port)
  - `TunnelAssignmentResponse` (assigned_port, remote_host)
  - Add input validation and constraints

### Step 8: API Handlers & Business Logic
- [ ] Create `app/api/handlers.py`:
  - `handle_client_registration(request)`:
    - Validate public key format
    - Store client in database
    - Assign unique port (find next available port)
    - Encrypt and store private key (if provided)
    - Return assigned port and client ID
  - `handle_authentication(client_id, auth_data)`:
    - Verify client exists
    - Check signature/credentials
    - Return authentication token or status
  - `handle_service_pre_config(client_id)`:
    - Retrieve client info
    - Assign port if not already assigned
    - Return configuration details
  - `handle_service_install(client_id)`:
    - Generate systemd service file
    - Return service file content
  - `handle_service_status(client_id)`:
    - Check tunnel status
    - Return connected/disconnected state

### Step 9: API Routes
- [ ] Create `app/api/routes.py`:
  - `POST /register` - client registration
  - `POST /auth` - client authentication
  - `POST /service/pre` - prepare service configuration
  - `GET /service/systemd/{client_id}` - retrieve systemd service file
  - `POST /service/install` - install service on client
  - `GET /service/status/{client_id}` - check tunnel status
  - `GET /health` - health check endpoint
  - Add error handling and response formatting

### Step 10: Main FastAPI Application
- [ ] Create `app/__init__.py` or `app/main.py`:
  - Initialize FastAPI app
  - Load configuration
  - Initialize database
  - Register routes
  - Setup middleware (logging, CORS if needed)
  - Error handling middleware

### Step 11: Start Server Script
- [ ] Create `scripts/start_server.py`:
  - Parse command-line arguments
  - Load environment variables
  - Initialize database migrations
  - Start Uvicorn server with appropriate settings
  - Add graceful shutdown handling

---

## Phase 4: Utility Functions (Week 3)

### Step 12: Utility Modules
- [ ] Create `app/utils/ip_utils.py`:
  - `get_client_ip_address(request)` - extract client IP from request
  - `validate_ip_address(ip_string)` - validate IP format
  - `resolve_hostname(hostname)` - DNS lookup
- [ ] Create `app/utils/port_utils.py`:
  - `get_next_available_port(start_port, max_port)` - find available port
  - `is_port_available(port)` - check if port is in use
  - `validate_port_range(port)` - ensure port is in allowed range

---

## Phase 5: Testing (Week 3-4)

### Step 13: Unit Tests
- [ ] Create `tests/test_models.py`:
  - Test Client model creation and validation
  - Test SSHKey model and encryption
  - Test TunnelAssignment model
- [ ] Create `tests/test_security.py`:
  - Test encryption/decryption functions
  - Test key validation functions
  - Test edge cases (invalid keys, malformed data)
- [ ] Create `tests/test_ssh_manager.py`:
  - Test SSH key loading
  - Test authorized_keys file manipulation
  - Test restricted command generation
- [ ] Create `tests/test_service_manager.py`:
  - Test systemd service file generation
  - Validate service file syntax
  - Test template rendering

### Step 14: Integration Tests
- [ ] Create `tests/test_api.py`:
  - Test `/register` endpoint
  - Test `/auth` endpoint
  - Test `/service/pre` endpoint
  - Test `/service/systemd/{client_id}` endpoint
  - Test error responses and validation
- [ ] Test database transactions
- [ ] Test concurrent client registrations

### Step 15: Testing Infrastructure
- [ ] Setup pytest configuration (`pytest.ini`)
- [ ] Create test fixtures and factories
- [ ] Setup test database (SQLite in-memory)
- [ ] Add test coverage reporting
- [ ] Create CI/CD pipeline (GitHub Actions, GitLab CI, etc.)

---

## Phase 6: Security Hardening (Week 4)

### Step 16: Enhanced Security
- [ ] Implement HTTPS/TLS for API communication
- [ ] Add rate limiting to prevent brute-force attacks
- [ ] Implement request signing/verification
- [ ] Add audit logging for all operations
- [ ] Secure secret management (use Vault or environment variables)
- [ ] Implement key rotation strategy
- [ ] Add CSRF protection
- [ ] SQL injection prevention review

### Step 17: Key Management Best Practices
- [ ] Implement secure key storage (HSM integration if available)
- [ ] Add key expiration/renewal logic
- [ ] Create key backup procedures
- [ ] Document key lifecycle management
- [ ] Implement key access logging

---

## Phase 7: Deployment & Containerization (Week 4-5)

### Step 18: Docker Setup
- [ ] Create `Dockerfile`:
  - Use Python 3.11+ base image
  - Install system dependencies
  - Install Python dependencies
  - Expose port for API
  - Set entry point to start_server.py
- [ ] Create `docker-compose.yml`:
  - Define API service
  - Define database service (PostgreSQL if desired)
  - Setup networking and volumes
  - Environment variable configuration

### Step 19: Deployment Scripts
- [ ] Create `scripts/deploy_server.sh`:
  - Pull latest code
  - Build Docker image
  - Run migrations
  - Start container
- [ ] Create `scripts/deploy_client.sh`:
  - Download systemd service file
  - Install service file
  - Create SSH config entries
  - Enable and start service
- [ ] Create `scripts/cleanup.sh`:
  - Remove old services
  - Cleanup database records
  - Archive logs

### Step 20: Documentation
- [ ] Update `README.md`:
  - Installation instructions
  - Quick start guide
  - Configuration reference
  - API documentation
  - Troubleshooting guide
- [ ] Create `DEPLOYMENT.md`:
  - Server deployment steps
  - Client installation guide
  - Monitoring setup
  - Backup procedures
- [ ] Create `API_REFERENCE.md`:
  - Endpoint documentation
  - Request/response examples
  - Error codes
  - Rate limits

---

## Phase 8: Monitoring & Maintenance (Week 5+)

### Step 21: Monitoring & Logging
- [ ] Setup centralized logging (ELK, Splunk, or CloudWatch)
- [ ] Create monitoring dashboards
- [ ] Set up alerting for:
  - Connection failures
  - Port conflicts
  - Database errors
  - High CPU/Memory usage
- [ ] Implement health check endpoints with detailed status

### Step 22: Maintenance & Operations
- [ ] Create database backup scripts
- [ ] Document incident response procedures
- [ ] Create disaster recovery plan
- [ ] Setup log rotation
- [ ] Monitor SSH tunnel stability
- [ ] Track client connection metrics

---

## Implementation Priority & Dependencies

### Critical Path (Must Complete First):
1. Step 1: Project Structure
2. Step 2: Configuration
3. Step 3: Database Models
4. Step 4: Encryption
5. Step 7: API Schemas
6. Step 8: API Handlers
7. Step 9: API Routes
8. Step 10: Main Application

### Can Be Parallelized:
- Step 5: SSH Manager (after Step 4)
- Step 6: Service Manager (after Step 3)
- Step 12: Utility modules (independent)
- Step 13-15: Testing (after main code)

### Post-Core Implementation:
- Step 16-17: Security hardening
- Step 18-20: Deployment & documentation
- Step 21-22: Monitoring

---

## Checkpoints & Milestones

### Checkpoint 1 (End of Week 1):
- Project structure created
- Configuration system working
- Database models defined and migrated
- Encryption/decryption functional
- SSH manager basic functionality complete

### Checkpoint 2 (End of Week 2):
- API schemas defined
- All API endpoints stubbed
- Handlers implementing business logic
- Registration and authentication flow working
- Service file generation functional

### Checkpoint 3 (End of Week 3):
- All API endpoints fully functional
- Utility modules complete
- Unit tests written and passing
- Integration tests for API working

### Checkpoint 4 (End of Week 4):
- Security hardening complete
- All tests passing with good coverage
- Docker containers ready
- Documentation complete

### Checkpoint 5 (Ongoing):
- Deployment successful
- Monitoring active
- Performance optimized
- Production-ready

---

## Success Criteria

- [ ] All API endpoints respond with correct status codes
- [ ] Client registration and authentication workflow complete
- [ ] SSH keys properly encrypted and validated
- [ ] Systemd service files generate correctly
- [ ] Reverse SSH tunnels establish successfully
- [ ] Test coverage >80%
- [ ] No security vulnerabilities in pen testing
- [ ] Deployment runs without errors
- [ ] Monitoring and logging functional
- [ ] Documentation complete and clear
