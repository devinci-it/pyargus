# Encryption Key Management Guide

## Overview

PyArgus handles encryption keys differently in **development** vs **production** environments to balance security and developer experience.

## Development Environment

### Automatic Key Generation
- Leave `ENCRYPTION_KEY` empty in `.env` (or not set)
- PyArgus will **automatically generate** a random development key on startup
- This key is **not persisted** - regenerated on each restart
- **Safe for development** - no sensitive data

### Setup
```bash
# .env
ENVIRONMENT=development
ENCRYPTION_KEY=  # Leave empty - auto-generated

# Or omit ENCRYPTION_KEY entirely
```

### How it works
```python
from pyargus import app, initialize_app

# Initialize app
my_app = initialize_app()

# Encryption key is automatically generated for development
print(my_app.config.security.encryption_key)  # Random base64-encoded key
```

## Production Environment

### Requirements
- **NEVER** use auto-generated keys in production
- **MUST** explicitly set `ENCRYPTION_KEY` environment variable
- PyArgus will **fail to start** if:
  - `ENVIRONMENT=production` AND
  - `ENCRYPTION_KEY` is empty

### Option 1: Environment Variable (Recommended for Small Deployments)

```bash
# Set as environment variable
export ENCRYPTION_KEY="your-base64-encoded-key-here"
export ENVIRONMENT=production

# Start app
pyargus
```

### Option 2: Docker Secrets (Recommended for Docker/Kubernetes)

#### Docker
```dockerfile
# Dockerfile
FROM python:3.12

WORKDIR /app
COPY . .

RUN pipenv install --deploy

ENV ENVIRONMENT=production

# Secret will be provided at runtime
CMD ["pipenv", "run", "pyargus"]
```

```bash
# docker-compose.yml
services:
  pyargus:
    build: .
    environment:
      - ENVIRONMENT=production
      - ENCRYPTION_KEY_FILE=/run/secrets/encryption_key
    secrets:
      - encryption_key
    command: pipenv run pyargus

secrets:
  encryption_key:
    file: ./secrets/encryption_key.txt
```

#### Kubernetes
```yaml
# k8s-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: pyargus-secrets
type: Opaque
data:
  encryption-key: <base64-encoded-key>

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pyargus
spec:
  containers:
  - name: pyargus
    image: pyargus:latest
    env:
    - name: ENVIRONMENT
      value: "production"
    - name: ENCRYPTION_KEY
      valueFrom:
        secretKeyRef:
          name: pyargus-secrets
          key: encryption-key
```

### Option 3: Key Management Service (AWS KMS, Vault, etc.)

For enterprise deployments, fetch the key at runtime:

```python
# config.py or bootstrap.py
import os
import boto3

def get_encryption_key_from_kms():
    """Fetch encryption key from AWS KMS."""
    region = os.getenv('AWS_REGION', 'us-east-1')
    secret_arn = os.getenv('KMS_SECRET_ARN')
    
    client = boto3.client('secretsmanager', region_name=region)
    response = client.get_secret_value(SecretId=secret_arn)
    
    return response['SecretString']

# Then in config
if os.getenv('USE_KMS_SECRETS'):
    encryption_key = get_encryption_key_from_kms()
else:
    encryption_key = os.getenv('ENCRYPTION_KEY', '')
```

## Generating Encryption Keys

### Generate a new key

```python
import base64
import os

# Generate a random 32-byte key and encode to base64
key = base64.b64encode(os.urandom(32)).decode('utf-8')
print(f"ENCRYPTION_KEY={key}")
```

Or use command line:
```bash
python3 -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode('utf-8'))"
```

### Store securely

**Development:**
```
# .env (git-ignored)
ENCRYPTION_KEY=your-generated-key-here
```

**Production:**
- Use **secrets management system**
- **Never** commit to git
- **Never** share via chat/email
- **Rotate regularly** (monthly recommended)

## Environment Detection

PyArgus automatically detects the environment:

```python
from pyargus.core.config import AppConfig

config = AppConfig.from_env()

if config.environment == 'production':
    # Strict encryption key requirement
    # Must have ENCRYPTION_KEY set
else:
    # Development: auto-generate if missing
    # Auto-generated keys are NOT persisted
```

## Best Practices

### Development
✅ Leave `ENCRYPTION_KEY` empty
✅ Auto-generated key regenerates on restart
✅ Use git-ignored `.env` file
✅ Safe for CI/CD pipelines

### Production
✅ Set `ENCRYPTION_KEY` explicitly
✅ Use secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
✅ Rotate keys regularly (monthly)
✅ Never commit keys to git
✅ Use separate keys per environment
✅ Audit key access and rotation
✅ Use environment-specific secrets

## Troubleshooting

### "encryption_key is REQUIRED in production environment"
**Problem:** `ENCRYPTION_KEY` is not set in production
**Solution:** Set `ENCRYPTION_KEY` environment variable before starting

### Key rotation in production
**Approach:**
1. Create new key in secrets manager
2. Deploy new version with new key reference
3. Re-encrypt data with new key
4. Monitor for decryption errors

### Forgot the encryption key
**For Development:** No problem - auto-generates new one
**For Production:** 
- Data encrypted with old key may be inaccessible
- Keep backup of keys in secure location
- Test recovery procedures regularly

## Configuration Example

### Development (.env)
```
ENVIRONMENT=development
ENCRYPTION_KEY=
DEBUG=true
```

### Production (Environment Variables)
```
ENVIRONMENT=production
ENCRYPTION_KEY=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn==
DEBUG=false
```

## See Also

- [Configuration Documentation](./config.md)
- [Bootstrap Documentation](./bootstrap.md)
- [Security Best Practices](./security.md)
