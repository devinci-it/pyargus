#!/usr/bin/env python3
"""
PyArgus Main Entry Point.

This script serves as the single entry point for the PyArgus application.
It bootstraps the application using the ApplicationFactory pattern, loads
configuration from environment, and starts the API server.

Usage:
    python main.py
    python main.py --debug
    python main.py --port 9000
    python main.py --config /path/to/config.env
"""

import os
import sys
import argparse

# Add src to path for imports
sys.path.insert(0, 'src')

# ============================================================================
# BOOTSTRAP: Load environment and configure logger FIRST
# ============================================================================
def bootstrap_logger():
    """
    Bootstrap PyLogger from environment variables before importing main app.
    This must happen early to enable logging throughout the application.
    
    Returns:
        Logger: Configured logger instance
    """
    from dotenv import load_dotenv
    from pylogger import SettingsBuilder
    
    # Load environment variables
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("✓ Loaded environment from .env")
    
    # Configure logger from environment variables
    logger = (SettingsBuilder()
        .app_name(os.getenv('PYLOGGER_APP_NAME', 'PyArgus'))
        .development(os.getenv('PYLOGGER_DEVELOPMENT', 'true').lower() == 'true')
        .echo(os.getenv('PYLOGGER_ECHO', 'true').lower() == 'true')
        .level(os.getenv('PYLOGGER_LEVEL', 'DEBUG'))
        .log_dir(os.getenv('PYLOGGER_LOG_DIR', './logs'))
        .build())
    
    return logger

# Configure logger immediately at startup
logger = bootstrap_logger()

# Now we can use the logger throughout bootstrap
from pylogger import build_log_decorator

from pyargus import (
    Application,
    ApplicationFactory,
    AppConfig,
    ConfigurationError,
)


def load_dotenv_legacy(env_file: str = ".env") -> None:
    """Legacy function - dotenv now loaded in bootstrap_logger."""
    pass


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="PyArgus SSH Bastion Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start with default settings
  python main.py --debug            # Start in debug mode
  python main.py --port 9000        # Start on custom port
  python main.py --environment prod # Load production configuration
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=".env",
        help="Path to .env configuration file (default: .env)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="API port (overrides config)"
    )
    parser.add_argument(
        "--host",
        type=str,
        help="API host (overrides config)"
    )
    parser.add_argument(
        "--environment",
        type=str,
        choices=["development", "staging", "production"],
        help="Environment (overrides config)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="Number of API workers (overrides config)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="PyArgus 0.1.0"
    )
    
    return parser.parse_args()


def create_app_config(args: argparse.Namespace) -> AppConfig:
    """
    Create application configuration from arguments and environment.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        AppConfig: Application configuration
    """
    # Load initial config from environment
    config = AppConfig.from_env()
    
    # Override with command-line arguments
    if args.debug:
        config.debug = True
        config.api.debug = True
    
    if args.environment:
        config.environment = args.environment
    
    if args.port:
        config.api.port = args.port
    
    if args.host:
        config.api.host = args.host
    
    if args.workers:
        config.api.workers = args.workers
    
    return config


def main() -> int:
    """
    Main entry point for the application.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Create application configuration
        config = create_app_config(args)
        
        # Log startup information using the pre-configured logger
        startup_msg = f"""
{'='*60}
  {config.app_name} v{config.version}
{'='*60}
Environment: {config.environment}
Debug Mode: {config.debug}
API: {config.api.host}:{config.api.port}
Workers: {config.api.workers}
Database: {config.database.database_url}
{'='*60}
"""
        print(startup_msg)
        logger.info(f"Starting {config.app_name} v{config.version}")
        logger.debug(f"Environment: {config.environment}")
        logger.debug(f"Debug Mode: {config.debug}")
        logger.debug(f"API: {config.api.host}:{config.api.port}")
        
        # Create and initialize application
        print("Initializing application...")
        logger.info("Initializing application")
        app = ApplicationFactory.create(config)
        ApplicationFactory.set_instance(app)
        app.initialize()
        
        logger.info("Application initialized successfully")
        logger.debug("Application is ready to serve")
        
        print("✓ Application initialized successfully")
        print(f"✓ Application is ready to serve")
        print(f"\nAPI Server is running at http://{config.api.host}:{config.api.port}")
        print("Press Ctrl+C to stop the server\n")
        
        logger.info(f"API Server listening at http://{config.api.host}:{config.api.port}")
        
        # TODO: Start FastAPI server here
        # This is where uvicorn.run() would be called
        # uvicorn.run("app.api.routes:app", host=config.api.host, port=config.api.port, reload=config.api.reload)
        
        return 0
        
    except ConfigurationError as e:
        error_msg = f"Configuration Error: {e.message} (Error Code: {e.error_code})"
        logger.error(error_msg)
        print(f"\n❌ {error_msg}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\nShutdown signal received...")
        logger.info("Shutdown signal received")
        if ApplicationFactory.get_instance():
            logger.info("Shutting down application")
            print("Shutting down application...")
            ApplicationFactory.get_instance().shutdown()
        logger.info("Application shutdown completed")
        print("✓ Application shutdown completed")
        return 0
    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(f"\n❌ {error_msg}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
