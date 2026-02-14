## **Complete Proposal/Plan for the SSH Bastion App ("PyArgus")**

### **Objective**:

Develop a centralized SSH Bastion server application, named **"PyArgus"**, that manages secure SSH connections for clients by creating persistent SSH reverse tunnels. The server will register and authenticate clients, securely store their SSH keys, and manage systemd service files to automate SSH tunnel creation for each client.

### **High-Level Features**:

1. **Registration**: Clients register by sending a request with their SSH public key, which is securely stored in the server's database.
2. **Key Management**: The server stores public keys, validates them, and encrypts private keys with a symmetric encryption algorithm.
3. **Reverse SSH Tunnels**: Clients are assigned remote ports for reverse SSH tunneling. Each client will use a unique port (e.g., `9221`, `9222`, etc.).
4. **Service Generation**: The server will generate and deploy a custom systemd service file (`ssh-az-bastion.service`) to the client for automated SSH tunneling.
5. **API-based Communication**: REST API for client registration, authentication, service installation, and SSH management.
6. **Security**: The server will handle SSH key encryption and decryption, as well as key verification to prevent unauthorized access.

---

### **Architecture**:

1. **Core Application (PyArgus)**:

   * **Models** (Database): Using **Peewee ORM** to manage client records, SSH keys, and associated metadata.
   * **API**: The RESTful API (built with **FastAPI** or **Flask**) allows clients to register, authenticate, and manage services.
   * **SSH Manager**: Manages key validation, adds public keys to the authorized keys file, and initiates SSH connections.
   * **Service Manager**: Generates and installs systemd service files (`ssh-az-bastion.service`) to automate the SSH reverse tunnel creation on the client machine.
   * **Security**: Encrypts/decrypts client keys using a symmetric encryption algorithm (e.g., AES) with a shared secret.

2. **Systemd Service**:

   * Clients will install a systemd service (`ssh-az-bastion.service`) that ensures the reverse SSH tunnel is maintained persistently on the client system.

3. **Database**:

   * **Peewee ORM** will be used to handle client data and key management.
   * **Schema**: Each client record will include information such as:

     * Client ID
     * Hostname
     * IP address
     * Public key (stored securely as a hash)
     * Assigned local and remote ports for SSH tunneling
     * Encrypted private key

4. **API Endpoints**:

   * **/register**: Client registration (public key, identification data).
   * **/auth**: Authentication for clients.
   * **/service/install**: Returns a systemd service file for client installation.
   * **/service/pre**: Prepares necessary configurations for the client (e.g., port assignments).
   * **/service/systemd**: Returns the systemd service file template to be deployed.

---

### **Project Structure**:

```plaintext
pyargus/
│
├── app/                         # Core application code
│   ├── __init__.py              # Initializes the app package
│   ├── config.py                # App-wide configuration settings
│   ├── models.py                # Database models (Peewee ORM)
│   ├── ssh_manager.py           # SSH-related functionalities (key management, SSH tunneling)
│   ├── service_manager.py       # Service-related tasks (systemd, service file generation)
│   ├── api/                     # REST API implementation
│   │   ├── __init__.py          # Initializes the API module
│   │   ├── routes.py            # Define API routes (registration, authentication, etc.)
│   │   ├── schemas.py           # Request/Response schemas (Pydantic for FastAPI, Marshmallow for Flask)
│   │   └── handlers.py          # Handle API logic (validation, key management, etc.)
│   ├── security/                # Security-related logic (encryption, key validation)
│   │   ├── __init__.py
│   │   ├── encryption.py        # Symmetric encryption/decryption (AES, etc.)
│   │   └── key_validator.py     # Key validation logic
│   └── utils/                   # Utility functions and helpers
│       ├── __init__.py
│       └── ip_utils.py          # Utility functions for IP address lookup, etc.
│
├── migrations/                  # Database migrations (Peewee)
│   ├── 001_initial_schema.py    # Initial migration for database schema
│   └── ...
│
├── scripts/                     # Command-line and system setup scripts
│   ├── setup.sh                 # Setup for environment, dependencies, etc.
│   ├── start_server.py          # Script to start the API server
│   └── deploy_client.sh         # Deployment script to install systemd service
│
├── tests/                       # Unit and integration tests
│   ├── __init__.py
│   ├── test_models.py           # Test the models (client registration, key storage)
│   ├── test_ssh_manager.py      # Test SSH manager (tunneling, key verification)
│   ├── test_api.py              # Test API endpoints (registration, service generation)
│   └── test_security.py         # Test security logic (encryption, key validation)
│
├── requirements.txt             # Project dependencies (Flask/FastAPI, Peewee, etc.)
├── Dockerfile                   # Docker container configuration
├── .env                         # Environment variables (e.g., database URLs, API keys)
└── README.md                    # Project documentation
```

---

### **Detailed App Flow**:

1. **Client Registration**:

   * The client sends a POST request to `/register` with its public SSH key and other metadata (e.g., hostname, IP).
   * The server verifies the key and stores the public key hash in the database.
   * The server generates a **unique port** for the client (e.g., `9221`, `9222`) and assigns it.
   * The client receives a response containing its **unique remote port** and **encrypted private key** (using symmetric encryption) that will be stored on the client side.

2. **SSH Key Management**:

   * The server adds the **client's public key** to its **authorized_keys** file with restrictions (e.g., only allowing specific ports).
   * **Key verification** is done to ensure the client is authenticated.

3. **Systemd Service Generation**:

   * The server creates a custom `systemd` service file (`ssh-az-bastion.service`) for the client, which contains the reverse SSH tunneling configuration:

     ```bash
     # /etc/systemd/system/ssh-az-bastion.service
     [Unit]
     Description=SSH Reverse Tunnel to Bastion

     [Service]
     User=hawking
     ExecStart=/usr/bin/ssh -F /home/hawking/.ssh/config -N -T -R 9221:127.0.0.1:22 bastion.az.ubuntujj
     Restart=always
     RestartSec=10

     [Install]
     WantedBy=multi-user.target
     ```
   * This file is sent to the client for installation using the `/service/install` API endpoint.

4. **Client-Side Configuration**:

   * The client installs the systemd service and enables it to run automatically on boot.

5. **Service Management**:

   * The server listens for service requests and can generate a new service configuration if needed.

6. **API Interaction**:

   * **Authentication**: The `/auth` endpoint allows clients to authenticate themselves using their registered public key.
   * **Service Pre-configuration**: The `/service/pre` endpoint ensures the necessary configurations are set up on the client side (e.g., port assignment).
   * **Service Installation**: The `/service/install` endpoint provides the `systemd` service file to be installed on the client.

---

### **Security Considerations**:

1. **Key Management**:

   * Client private keys are stored encrypted with a symmetric key (AES) on the server.
   * The server uses a secure method to decrypt the private keys during SSH tunnel creation.
   * Public keys are stored in a hash format to prevent direct access.

2. **SSH Key Restrictions**:

   * When adding public keys to the **authorized_keys** file, restrictions such as `no-pty`, `no-agent-forwarding`, and a specific port range are set to prevent misuse.

3. **Symmetric Encryption**:

   * The server will use **AES encryption** to encrypt and store client private keys securely.

---

### **Tech Stack**:

* **Backend**: Python (Flask or FastAPI for the API server)
* **Database**: Peewee ORM with SQLite/PostgreSQL
* **SSH**: Paramiko (Python SSH library) for SSH key management and reverse tunneling
* **Security**: PyCryptodome for symmetric encryption
* **Systemd**: For managing the reverse tunnel service on client systems
* **Containerization**: Docker for easy deployment and scaling

---

### **Development Plan**:

#### **Phase 1: Core Functionality**

* Develop basic SSH key management and reverse tunneling functionality in `ssh_manager.py`.
* Implement **client registration** and **key storage**


in the database.

* Implement **service generation** and API endpoints (`/register`, `/auth`, `/service/install`).
* Set up **systemd service file** creation for client-side installation.

#### **Phase 2: Security & Testing**

* Implement **encryption/decryption** for private keys.
* Secure the communication between server and clients (SSL/TLS).
* Write unit tests for models, API endpoints, and SSH manager.
* Perform penetration testing to ensure no security vulnerabilities (especially in key management).

#### **Phase 3: Deployment**

* Deploy the server using Docker or directly on a host machine.
* Deploy client-side systemd services for reverse tunnel automation.
* Monitor the system's performance and security on an ongoing basis.

---

### **Timeline Estimate**:

1. **Phase 1**: 2-3 weeks for core functionality and basic testing.
2. **Phase 2**: 2 weeks for security hardening, key management, and testing.
3. **Phase 3**: 1-2 weeks for deployment, documentation, and final testing.

---

### **Conclusion**:

**PyArgus** aims to create a highly secure, centralized SSH Bastion system that efficiently manages SSH reverse tunneling for multiple clients. By using secure key management, symmetric encryption, and systemd automation, we ensure that clients' SSH connections are persistent, controlled, and easy to manage. The use of REST APIs will allow easy integration and scalability for future improvements.
