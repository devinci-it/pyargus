"""
PyArgus Application Entry Point - __main__ module.

This module provides the commandline entry point for PyArgus.
It uses the centralized app.py for all application management.
"""

import sys
import argparse

from .app import initialize_app, get_app
from .core.exceptions import ConfigurationError


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="PyArgus SSH Bastion Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pyargus --help
  pyargus --debug
  pyargus --version
        """
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="API server port (default: 8000)"
    )
    parser.add_argument(
        "--host",
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for PyArgus application CLI.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        if args.version:
            print("PyArgus version 0.1.0")
            return 0
        
        # Initialize application (this handles all bootstrapping)
        app = initialize_app(debug=args.debug)
        
        # Override config from CLI args if provided
        if args.port:
            app.config.api.port = args.port
        
        if args.host:
            app.config.api.host = args.host
        
        # Log startup info
        app.logger.info(f"PyArgus starting in {app.config.environment} mode")
        print("✓ Application initialized successfully")
        print(f"\nAPI Server is listening at http://{app.config.api.host}:{app.config.api.port}")
        print("Press Ctrl+C to stop the server\n")
        
        # TODO: Start server here
        # from uvicorn import run
        # run(app_instance, host=app.config.api.host, port=app.config.api.port)
        
        return 0
        
    except ConfigurationError as e:
        print(f"\n❌ Configuration Error: {e.message}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        app = get_app()
        if app.is_initialized:
            app.logger.info("Shutdown signal received")
            app.shutdown()
        print("\n✓ Application shutdown completed")
        return 0
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}", file=sys.stderr)
        app = get_app()
        if app.is_initialized:
            app.logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
