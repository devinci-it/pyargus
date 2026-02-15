#!/usr/bin/env python
"""
PyArgus Database Initialization Script

Creates and initializes the SQLite database with all required tables.

Usage:
    python setup_database.py              # Initialize with default path
    python setup_database.py --reset      # Drop all tables and reinitialize
    python setup_database.py --path path/to/db.db  # Custom database path
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pyargus.core import init_database, create_tables, get_database, close_database
from pyargus.core.models import Client, SSHKey, TunnelAssignment, ServiceStatus

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def reset_database():
    """Drop all tables from the database."""
    logger.info("Dropping all tables...")
    db = get_database()
    
    # Drop in reverse dependency order
    db.drop_tables([ServiceStatus, TunnelAssignment, SSHKey, Client], safe=True)
    logger.info("✓ All tables dropped")


def init_db(db_path=None, reset=False):
    """
    Initialize the database with all tables.
    
    Args:
        db_path: Optional path to database file
        reset: If True, drop existing tables first
    """
    logger.info("=" * 80)
    logger.info("PyArgus Database Initialization")
    logger.info("=" * 80)
    
    # Initialize database
    logger.info("Initializing database connection...")
    db = init_database(db_path)
    logger.info(f"✓ Database initialized at: {db.database}")
    
    # Reset if requested
    if reset:
        reset_database()
    
    # Create tables
    logger.info("Creating tables...")
    create_tables()
    logger.info("✓ Tables created successfully")
    
    # Display table info
    logger.info("\nDatabase Tables:")
    logger.info(f"  - Client (clients table)")
    logger.info(f"  - SSHKey (ssh_keys table)")
    logger.info(f"  - TunnelAssignment (tunnel_assignments table)")
    logger.info(f"  - ServiceStatus (service_status table)")
    
    logger.info("\n" + "=" * 80)
    logger.info("✓ Database initialization completed successfully")
    logger.info("=" * 80)
    
    # Close database
    close_database()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Initialize PyArgus database with all required tables'
    )
    parser.add_argument(
        '--path',
        type=str,
        default=None,
        help='Path to database file (default: ./pyargus.db)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Drop existing tables before creating new ones'
    )
    
    args = parser.parse_args()
    
    try:
        init_db(db_path=args.path, reset=args.reset)
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        sys.exit(1)
