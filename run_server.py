#!/usr/bin/env python3
"""
PyArgus Flask API Server - Main Entry Point.

Starts the Flask API server with all routes registered.

Usage:
    python run_server.py
    python run_server.py --host 0.0.0.0 --port 5000 --debug
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for the application
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG', 'false').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pyargus.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('pyargus')


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configure app
    app.config['DEBUG'] = os.getenv('DEBUG', 'false').lower() == 'true'
    app.config['JSON_SORT_KEYS'] = False
    
    logger.info("Flask app created")
    
    # Register API blueprint
    from pyargus.api import api_blueprint
    app.register_blueprint(api_blueprint)
    logger.info("API blueprint registered")
    
    # Add health check root endpoint
    @app.route('/')
    def root():
        """Root health check endpoint."""
        return {
            'status': 'ok',
            'service': 'PyArgus SSH Bastion',
            'version': '0.1.0',
            'api_docs': '/api/health'
        }, 200
    
    logger.info("Root endpoint registered")
    
    return app


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='PyArgus Flask API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Server port (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("PyArgus API Server Starting")
    logger.info("=" * 80)
    
    try:
        # Create Flask app
        app = create_app()
        
        logger.info(f"Starting server on {args.host}:{args.port}")
        print(f"\n✓ PyArgus API Server")
        print(f"  Host: http://{args.host}:{args.port}")
        print(f"  Debug: {args.debug}")
        print(f"\n  Available endpoints:")
        print(f"    GET  /              - Health check")
        print(f"    GET  /api/health    - API health check")
        print(f"    POST /api/register  - Register client")
        print(f"    POST /api/auth      - Authenticate client")
        print(f"    GET  /api/clients   - List clients")
        print(f"\n  Press Ctrl+C to stop\n")
        
        # Run the server
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or os.getenv('DEBUG', 'false').lower() == 'true',
            use_reloader=args.debug
        )
        
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
        print("\n✓ Server stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
