# app/api/ - REST API Module

Location: `/app/api/`

## Purpose

REST API implementation for PyArgus. Provides HTTP endpoints for client registration, authentication, and service management using FastAPI framework with Pydantic schemas.

## Module Structure

```
app/api/
├── __init__.py      # Package initialization
├── routes.py        # API endpoints (to be implemented)
├── schemas.py       # Pydantic request/response models
└── handlers.py      # Business logic handlers
```

## submodules

### schemas.py
Pydantic models for request/response validation.

**Planned Schemas**:

```python
# Request schemas
class ClientRegistrationRequest(BaseModel):
    hostname: str
    ip_address: str
    public_key: str

class ClientAuthRequest(BaseModel):
    client_id: str
    signature: str
    timestamp: int

class ServiceInstallRequest(BaseModel):
    client_id: str

# Response schemas
class ClientRegistrationResponse(BaseModel):
    client_id: str
    assigned_port: int
    message: str

class ServiceInstallResponse(BaseModel):
    service_file_content: str
    assigned_port: int

class HealthCheckResponse(BaseModel):
    status: str
    services: Dict[str, str]
    version: str
```

**Features**:
- Input validation via Pydantic
- Automatic OpenAPI schema generation
- Type hints for IDE support
- JSON serialization/deserialization

### handlers.py
Business logic for API operations.

**Planned Handlers**:

```python
async def handle_client_registration(request: ClientRegistrationRequest) -> ClientRegistrationResponse:
    """
    Register a new client.
    
    1. Validate public key
    2. Check for duplicates
    3. Assign port
    4. Store in database
    5. Return details
    """
    pass

async def handle_authentication(request: ClientAuthRequest) -> AuthResponse:
    """
    Authenticate client.
    
    1. Verify client exists
    2. Check signature
    3. Generate token
    4. Return auth status
    """
    pass

async def handle_service_pre_config(client_id: str) -> ServicePreResponse:
    """
    Prepare service configuration.
    
    1. Get client info
    2. Assign port if needed
    3. Prepare configurations
    4. Return setup details
    """
    pass

async def handle_service_install(request: ServiceInstallRequest) -> ServiceInstallResponse:
    """
    Generate systemd service file.
    
    1. Get client configuration
    2. Generate service file
    3. Return for installation
    """
    pass

async def handle_service_status(client_id: str) -> StatusResponse:
    """
    Check tunnel status.
    
    1. Get client status
    2. Check SSH connection
    3. Return status details
    """
    pass
```

### routes.py
API endpoint definitions.

**Planned Endpoints**:

```python
# Registration and Authentication
POST   /register           # Register new client
POST   /auth               # Authenticate client
GET    /health             # Health check

# Service Management
POST   /service/pre        # Pre-configuration
GET    /service/systemd/{client_id}  # Get systemd file
POST   /service/install    # Install service
GET    /service/status/{client_id}   # Check status

# Admin Operations (future)
GET    /clients            # List all clients
GET    /clients/{client_id}  # Get client details
DELETE /clients/{client_id}  # Delete client
```

**Example Route**:

```python
from fastapi import APIRouter, HTTPException, status
from pyargus.api.schemas import ClientRegistrationRequest, ClientRegistrationResponse
from pyargus.api.handlers import handle_client_registration

router = APIRouter(prefix="/api", tags=["clients"])

@router.post("/register", response_model=ClientRegistrationResponse)
async def register_client(request: ClientRegistrationRequest):
    """Register a new SSH tunnel client."""
    try:
        result = await handle_client_registration(request)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PyArgusException as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## FastAPI Integration

### Application Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyargus.api.routes import router

app = FastAPI(
    title="PyArgus",
    description="SSH Bastion Server",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
```

### Running Server

```bash
# Development
uvicorn app.api:app --reload --port 8000

# Production
uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 4
```

## Error Handling

Map PyArgus exceptions to HTTP responses:

```python
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pyargus import PyArgusException, ValidationError

@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "field": exc.field,
            "code": exc.error_code
        }
    )

@app.exception_handler(PyArgusException)
async def pyargus_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message,
            "code": exc.error_code
        }
    )
```

## Request/Response Examples

### Register Client
```bash
POST /api/register

Request:
{
    "hostname": "client1.example.com",
    "ip_address": "192.168.1.100",
    "public_key": "ssh-rsa AAAA..."
}

Response (201):
{
    "client_id": "c123456",
    "assigned_port": 9221,
    "message": "Client registered successfully"
}

Response (409):
{
    "error": "Client already exists",
    "code": "CONFLICT"
}
```

### Authenticate
```bash
POST /api/auth

Request:
{
    "client_id": "c123456",
    "signature": "...",
    "timestamp": 1644820000
}

Response (200):
{
    "status": "authenticated",
    "token": "eyJ..."
}
```

### Get Service File
```bash
GET /api/service/systemd/c123456

Response (200):
{
    "service_file_content": "[Unit]\nDescription=...\n[Service]\n..."
}
```

### Health Check
```bash
GET /api/health

Response (200):
{
    "status": "healthy",
    "services": {
        "database": "ok",
        "ssh_manager": "ok"
    },
    "version": "0.1.0"
}
```

## Authentication & Authorization

### Token-based Auth
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    token = credentials.credentials
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
```

### Protected Routes
```python
@app.get("/protected")
async def protected_route(token: str = Depends(verify_token)):
    return {"message": "Authenticated"}
```

## Testing

```python
from fastapi.testclient import TestClient
from pyargus.api import app

client = TestClient(app)

def test_register_client():
    response = client.post("/api/register", json={
        "hostname": "test.example.com",
        "ip_address": "192.168.1.1",
        "public_key": "ssh-rsa AAAA..."
    })
    assert response.status_code == 201
    assert response.json()["client_id"] is not None

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## Documentation

FastAPI generates automatic documentation:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## Best Practices

1. **Use Pydantic models**: Automatic validation and docs
2. **Handle exceptions gracefully**: Convert to HTTP responses
3. **Return proper status codes**: 201 for created, 400 for bad request, etc.
4. **Document endpoints**: FastAPI docstrings appear in docs
5. **Use dependency injection**: Request, header, cookie dependencies
6. **Rate limit**: Protect from abuse
7. **Log requests**: Track API usage
8. **Validate input**: Pydantic does this automatically

## Status: Phase 3 Implementation

This module will be implemented in Phase 3 (REST API Implementation) as per the implementation plan.

## See Also

- [ARCHITECTURE.md](../ARCHITECTURE.md#project-directory-structure) - API structure
- [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md#adding-a-new-api-endpoint)
- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md#phase-3-rest-api-implementation-week-2-3)
