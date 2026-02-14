# app/security/ - Security & Encryption Module

Location: `/app/security/`

## Purpose

Handles security-related operations including encryption, decryption, and SSH key validation. Ensures all sensitive data is protected with strong encryption algorithms.

## Module Structure

```
app/security/
├── __init__.py              # Package initialization
├── encryption.py            # AES encryption/decryption (Phase 2)
└── key_validator.py         # SSH key validation (Phase 2)
```

## Planned Components

### encryption.py
Symmetric encryption/decryption using AES-256.

**Planned Functions**:

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    """
    Derive encryption key from password using PBKDF2.
    
    Args:
        password: Master encryption password
        salt: Optional salt (generates new if not provided)
    
    Returns:
        (key, salt) tuple
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_key(private_key_content: str, encryption_key: str) -> str:
    """
    Encrypt SSH private key using AES-256.
    
    Args:
        private_key_content: SSH private key content
        encryption_key: Master encryption key
    
    Returns:
        Base64-encoded encrypted key
    """
    key, salt = derive_key(encryption_key)
    fernet = Fernet(key)
    
    encrypted = fernet.encrypt(private_key_content.encode())
    # Store salt with encrypted data
    return base64.b64encode(salt + encrypted).decode()

def decrypt_key(encrypted_data: str, encryption_key: str) -> str:
    """
    Decrypt SSH private key using AES-256.
    
    Args:
        encrypted_data: Base64-encoded encrypted key
        encryption_key: Master encryption key
    
    Returns:
        Decrypted SSH private key content
    
    Raises:
        EncryptionError: If decryption fails
    """
    try:
        data = base64.b64decode(encrypted_data)
        salt = data[:16]
        encrypted = data[16:]
        
        key, _ = derive_key(encryption_key, salt)
        fernet = Fernet(key)
        
        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode()
    except Exception as e:
        raise EncryptionError(f"Failed to decrypt key: {str(e)}")
```

**Features**:
- AES-256 encryption via Fernet
- PBKDF2 key derivation
- Salt generation for security
- Base64 encoding for storage

**Usage**:
```python
from pyargus.security.encryption import encrypt_key, decrypt_key

# Encrypt a key
private_key_content = "-----BEGIN RSA PRIVATE KEY-----\n..."
master_key = "my-secret-encryption-key"

encrypted = encrypt_key(private_key_content, master_key)
print(encrypted)  # Base64-encoded encrypted data

# Decrypt later
decrypted = decrypt_key(encrypted, master_key)
assert decrypted == private_key_content
```

### key_validator.py
SSH key validation and format checking.

**Planned Functions**:

```python
def validate_ssh_key_format(key_content: str) -> bool:
    """
    Validate SSH public key format.
    
    Supported formats:
    - ssh-rsa AAAA...
    - ssh-ed25519 AAAA...
    - ecdsa-sha2-nistp256 AAAA...
    
    Args:
        key_content: SSH public key content
    
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^(ssh-rsa|ssh-ed25519|ecdsa-sha2-nistp256)\s+[A-Za-z0-9+/]+'
    return bool(re.match(pattern, key_content))

def validate_ssh_private_key(key_content: str) -> bool:
    """
    Validate SSH private key format.
    
    Supported formats:
    - RSA (-----BEGIN RSA PRIVATE KEY-----)
    - OpenSSH (-----BEGIN OPENSSH PRIVATE KEY-----)
    
    Args:
        key_content: SSH private key content
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        ValidationError: If key is invalid
    """
    if not key_content:
        raise ValidationError("Private key content is empty", field="private_key")
    
    valid_headers = [
        "-----BEGIN RSA PRIVATE KEY-----",
        "-----BEGIN OPENSSH PRIVATE KEY-----",
        "-----BEGIN EC PRIVATE KEY-----"
    ]
    
    if not any(header in key_content for header in valid_headers):
        raise ValidationError("Invalid private key format", field="private_key")
    
    return True

def extract_key_type(public_key: str) -> str:
    """
    Extract key type from SSH public key.
    
    Args:
        public_key: SSH public key content
    
    Returns:
        Key type (rsa, ed25519, ecdsa)
    """
    parts = public_key.split()
    if not parts:
        raise ValidationError("Invalid key format", field="public_key")
    
    key_type = parts[0]
    if key_type == "ssh-rsa":
        return "rsa"
    elif key_type == "ssh-ed25519":
        return "ed25519"
    elif key_type.startswith("ecdsa"):
        return "ecdsa"
    else:
        raise ValidationError(f"Unsupported key type: {key_type}", field="public_key")

def extract_fingerprint(public_key: str) -> str:
    """
    Calculate SHA256 fingerprint of public key.
    
    Args:
        public_key: SSH public key content
    
    Returns:
        SHA256 fingerprint in format: SHA256:xxxxx
    """
    from hashlib import sha256
    import base64
    
    parts = public_key.split()
    if len(parts) < 2:
        raise ValidationError("Invalid key format", field="public_key")
    
    key_blob = base64.b64decode(parts[1])
    fingerprint = base64.b64encode(sha256(key_blob).digest()).decode().rstrip("=")
    return f"SHA256:{fingerprint}"
```

**Features**:
- Format validation
- Key type detection
- Fingerprint calculation
- Error handling

**Usage**:
```python
from pyargus.security.key_validator import (
    validate_ssh_key_format,
    extract_key_type,
    extract_fingerprint
)

public_key = "ssh-rsa AAAA... user@host"

# Validate format
if validate_ssh_key_format(public_key):
    print("Valid SSH key")

# Get key type
key_type = extract_key_type(public_key)
print(f"Key type: {key_type}")

# Get fingerprint
fingerprint = extract_fingerprint(public_key)
print(f"Fingerprint: {fingerprint}")
```

## Integration with SSH Manager

Security module will be used by SSH Manager:

```python
from pyargus.security.encryption import encrypt_key, decrypt_key
from pyargus.security.key_validator import validate_ssh_key_format

class SSHManager(BaseService):
    def store_client_key(self, client_id, private_key_content):
        # Validate key
        validate_ssh_key_format(private_key_content)
        
        # Encrypt key
        encrypted = encrypt_key(private_key_content, self.encryption_key)
        
        # Store in database
        self.db.store_key(client_id, encrypted)
    
    def get_client_key(self, client_id):
        # Retrieve encrypted key
        encrypted = self.db.get_key(client_id)
        
        # Decrypt key
        private_key = decrypt_key(encrypted, self.encryption_key)
        
        return private_key
```

## Security Considerations

### Key Storage
- Private keys encrypted at rest
- Encryption key from environment (not in code)
- Salt added to prevent rainbow tables

### Key Rotation
- Implement regular key rotation
- Re-encrypt data with new key periodically
- Track key versions

### Audit Trail
- Log all encryption/decryption operations
- Monitor for unusual access patterns
- Alert on errors

### Best Practices
- Never log private key content
- Use strong encryption key (32+ chars)
- Validate all keys before storage
- Securely generate random values
- Use proper error handling

## Testing

```python
import pytest
from pyargus.security.encryption import encrypt_key, decrypt_key
from pyargus.security.key_validator import validate_ssh_key_format

def test_encrypt_decrypt():
    key_content = "-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----"
    encryption_key = "test-encryption-key"
    
    encrypted = encrypt_key(key_content, encryption_key)
    decrypted = decrypt_key(encrypted, encryption_key)
    
    assert decrypted == key_content

def test_ssh_key_validation():
    valid_key = "ssh-rsa AAAA... user@host"
    assert validate_ssh_key_format(valid_key)
    
    invalid_key = "invalid-key-format"
    assert not validate_ssh_key_format(invalid_key)
```

## Dependencies

```
pycryptodome==3.19.0
paramiko==3.4.0
```

## Status: Phase 2 Implementation

This module will be implemented in Phase 2 (Security & Encryption) as per the implementation plan.

## See Also

- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md#phase-2-security--encryption-layer-week-1-2)
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Security considerations
- [config.md](config.md) - Configuration for encryption key
