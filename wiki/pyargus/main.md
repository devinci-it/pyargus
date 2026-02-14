# main.py - Application Entry Point

Location: `/main.py`

## Purpose

Single, clear entry point for the PyArgus application. Handles command-line argument parsing, environment configuration loading, application bootstrap, and lifecycle management.

## Key Responsibilities

1. Parse command-line arguments
2. Load environment variables from .env file
3. Create application configuration
4. Initialize the application
5. Start the API server
6. Handle graceful shutdown

## Script Structure

```python
#!/usr/bin/env python3

# Imports
import os, sys, argparse
from pathlib import Path

from app import Application, ApplicationFactory, AppConfig, ConfigurationError

# Configuration
def load_dotenv(env_file: str) -> None: ...
def parse_arguments() -> argparse.Namespace: ...
def create_app_config(args: argparse.Namespace) -> AppConfig: ...

# Main function
def main() -> int: ...

# Entry point
if __name__ == "__main__":
    sys.exit(main())
```

## Command-Line Arguments

### Basic Usage
```bash
python main.py
```
Starts with default configuration.

### Debug Mode
```bash
python main.py --debug
```
Enables debug logging and auto-reload.

### Custom Port
```bash
python main.py --port 9000
```
Runs on specified port instead of default 8000.

### Custom Host
```bash
python main.py --host 127.0.0.1
```
Binds to specified host address.

### Environment Selection
```bash
python main.py --environment production
```
Loads production-specific configuration.

### Custom Workers
```bash
python main.py --workers 8
```
Runs with specified number of worker processes.

### Custom Configuration File
```bash
python main.py --config /etc/pyargus/.env
```
Loads environment from custom .env file.

### Help
```bash
python main.py --help
```
Shows all available options.

### Version
```bash
python main.py --version
```
Shows application version.

## Execution Flow

```
main.py
  ↓
parse_arguments()
  └─ Returns: Namespace with all CLI arguments
  ↓
load_dotenv(args.config)
  └─ Loads: Environment variables from file
  ↓
create_app_config(args)
  ├─ Loads config from environment
  ├─ Overrides with CLI arguments
  └─ Returns: AppConfig instance
  ↓
Print: Startup banner with configuration
  ↓
ApplicationFactory.create(config)
  ├─ Creates Application instance
  ├─ Initializes all components
  ├─ Registers core services
  └─ Returns: Ready-to-use Application
  ↓
ApplicationFactory.set_instance(app)
  └─ Stores: For global access
  ↓
Print: Success message and instructions
  ↓
[Ready to serve requests]
  ↓
Ctrl+C (KeyboardInterrupt)
  ↓
app.shutdown()
  └─ Cleanup: Close connections, release resources
  ↓
Exit: With status code 0 or 1
```

## Implementation Details

### 1. Environment Loading

```python
def load_dotenv(env_file: str = ".env") -> None:
    """
    Load environment variables from .env file.
    
    Supports:
    - .env (default)
    - Custom path: python main.py --config /etc/pyargus/.env
    
    Variables are merged with os.environ
    """
    if os.path.exists(env_file):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✓ Loaded environment from {env_file}")
        except ImportError:
            print(f"Warning: python-dotenv not installed")
```

### 2. Argument Parsing

```python
def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Namespace with:
        - config: Path to .env file
        - debug: Debug mode flag
        - port: API port
        - host: API host
        - environment: environment selection
        - workers: Number of workers
    """
    parser = argparse.ArgumentParser(
        description="PyArgus SSH Bastion Server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--config", type=str, default=".env")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--port", type=int)
    parser.add_argument("--host", type=str)
    parser.add_argument("--environment", choices=["development", "staging", "production"])
    parser.add_argument("--workers", type=int)
    parser.add_argument("--version", action="version", version="PyArgus 0.1.0")
    
    return parser.parse_args()
```

### 3. Configuration Creation

```python
def create_app_config(args: argparse.Namespace) -> AppConfig:
    """
    Create application configuration.
    
    Priority (highest to lowest):
    1. Command-line arguments
    2. Environment variables
    3. Defaults
    
    Example:
        python main.py --port 9000
        → Overrides env var DATABASE_URL with value from --config
        → Overrides default port 8000 with 9000
    """
    config = AppConfig.from_env()
    
    # Apply CLI overrides
    if args.debug:
        config.debug = True
        config.api.debug = True
    
    if args.port:
        config.api.port = args.port
    
    if args.host:
        config.api.host = args.host
    
    # ... more overrides ...
    
    return config
```

### 4. Startup Banner

```
============================================================
  PyArgus v0.1.0
============================================================
Environment: development
Debug Mode: False
API: 0.0.0.0:8000
Workers: 4
Database: sqlite:///pyargus.db
============================================================
```

### 5. Error Handling

```python
def main() -> int:
    try:
        # ... initialization ...
        return 0
        
    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e.message}")
        return 1
    
    except KeyboardInterrupt:
        print("\n\nShutdown signal received...")
        if app:
            app.shutdown()
        return 0
    
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
```

## Configuration Precedence

Settings are resolved in this order (first match wins):

1. **Command-line arguments**
   ```bash
   python main.py --port 9000
   ```

2. **Environment variables** (from .env file or system)
   ```bash
   export API_PORT=9000
   python main.py
   ```

3. **Default values** (in code)
   ```python
   APIConfig(port=8000)  # Default
   ```

## Typical Startup Scenarios

### Development
```bash
python main.py --debug
```
- Debug logging enabled
- Auto-reload on code changes
- Single worker

### Staging
```bash
python main.py --environment staging --port 8080
```
- Production config
- Custom port
- Multiple workers

### Production
```bash
python main.py --environment production --workers 8
```
- No debug output
- Optimized performance
- Multiple workers

### With Custom Config
```bash
python main.py --config /etc/pyargus/.env --environment production
```
- Load config from system directory
- Production environment
- Full configuration override capability

## Graceful Shutdown

When server receives SIGTERM or Ctrl+C:

```
1. Receives signal
2. Calls app.shutdown()
3. Services clean up:
   - Close database connections
   - Save pending operations
   - Release resources
4. Exit with code 0
```

## Exit Codes

- **0**: Successful execution
- **1**: Configuration error or unexpected exception

## Logging

Output goes to console with format:
```
2026-02-13 10:30:45 - PyArgus - INFO - Application initialized
```

Log level determined by `LOG_LEVEL` environment variable or `--debug` flag.

## Example: Custom Integration

```python
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app import ApplicationFactory

# Create application
app = ApplicationFactory.create()

# Now app is fully initialized and ready
config = app.config
logger = app.logger

logger.info(f"Running on {config.api.host}:{config.api.port}")
```

## Troubleshooting

### "Configuration Error: ENCRYPTION_KEY must be set"
**Solution**: Set in .env file or environment:
```bash
echo "ENCRYPTION_KEY=your-secret-key" >> .env
python main.py
```

### "API Server already in use"
**Solution**: Use different port:
```bash
python main.py --port 9000
```

### Application won't start
**Solution**: Enable debug mode for details:
```bash
python main.py --debug
```

## Best Practices

1. **Use for all startup**: Always use main.py, not direct imports
2. **Set environment variables**: Use .env for configuration
3. **Check return code**: Scripts should check `$?` after running
4. **Graceful shutdown**: Let app cleanup properly (Ctrl+C, not kill -9)
5. **Log output**: Redirect stdout/stderr for production runs

## See Also

- [ARCHITECTURE.md](wiki/ARCHITECTURE.md) - Architecture overview
- [config.md](wiki/pyargus/config.md) - Configuration module
- [application.md](wiki/pyargus/application.md) - Application class
- [DEVELOPER_GUIDE.md](wiki/DEVELOPER_GUIDE.md) - Development guide
