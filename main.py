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

from pyargus import Application, ApplicationFactory, AppConfig, ConfigurationError


def load_dotenv(env_file: str = ".env") -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file
    """
    if os.path.exists(env_file):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✓ Loaded environment from {env_file}")
        except ImportError:
            print(f"Warning: python-dotenv not installed, skipping .env file")
    else:
        print(f"Warning: {env_file} not found, using environment variables")


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
        
        # Load environment configuration
        load_dotenv(args.config)
        
        # Create application configuration
        config = create_app_config(args)
        
        # Print startup information
        print("\n" + "="*60)
        print(f"  {config.app_name} v{config.version}")
        print("="*60)
        print(f"Environment: {config.environment}")
        print(f"Debug Mode: {config.debug}")
        print(f"API: {config.api.host}:{config.api.port}")
        print(f"Workers: {config.api.workers}")
        print(f"Database: {config.database.database_url}")
        print("="*60 + "\n")
        
        # Create and initialize application
        print("Initializing application...")
        app = ApplicationFactory.create(config)
        ApplicationFactory.set_instance(app)
        
        print("✓ Application initialized successfully")
        print(f"✓ Application is ready to serve")
        print(f"\nAPI Server is running at http://{config.api.host}:{config.api.port}")
        print("Press Ctrl+C to stop the server\n")
        
        # TODO: Start FastAPI server here
        # This is where uvicorn.run() would be called
        # uvicorn.run("app.api.routes:app", host=config.api.host, port=config.api.port, reload=config.api.reload)
        
        return 0
        
    except ConfigurationError as e:
        print(f"\n❌ Configuration Error: {e.message}", file=sys.stderr)
        print(f"   Error Code: {e.error_code}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\nShutdown signal received...")
        if ApplicationFactory.get_instance():
            ApplicationFactory.get_instance().shutdown()
        print("✓ Application shutdown completed")
        return 0
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
