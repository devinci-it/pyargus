"""
Database initialization and Peewee ORM setup for PyArgus.

This module handles:
- Database connection configuration
- Model initialization
- Database migrations and schema creation
"""

import os
from pathlib import Path
from typing import Optional
from peewee import SqliteDatabase, Model

# Global database instance
_db: Optional[SqliteDatabase] = None


def get_database() -> SqliteDatabase:
    """
    Get or create the database instance.
    
    Returns:
        SqliteDatabase: The configured database instance
    """
    global _db
    if _db is None:
        _db = init_database()
    return _db


def init_database(db_path: Optional[str] = None) -> SqliteDatabase:
    """
    Initialize the database connection.
    
    Args:
        db_path: Optional path to database file. If not provided, uses default path.
        
    Returns:
        SqliteDatabase: Configured database instance
    """
    global _db
    
    if db_path is None:
        # Default to project root/pyargus.db
        db_path = os.getenv("DATABASE_URL", "sqlite:///./pyargus.db")
        # Convert sqlite:/// URL format to file path
        if db_path.startswith("sqlite:///"):
            db_path = db_path.replace("sqlite:///", "")
    
    # Ensure parent directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create database instance
    _db = SqliteDatabase(str(db_file))
    
    return _db


def close_database() -> None:
    """Close the database connection."""
    global _db
    if _db and not _db.is_closed():
        _db.close()
        _db = None


class BaseModel(Model):
    """
    Base model class for all Peewee models.
    
    Automatically uses the global database instance.
    """
    
    class Meta:
        database = get_database()
        legacy_table_names = False


def create_tables() -> None:
    """
    Create all model tables in the database.
    
    This should be called during application initialization.
    """
    from pyargus.core.models import Client, SSHKey, TunnelAssignment, ServiceStatus
    
    db = get_database()
    db.create_tables([Client, SSHKey, TunnelAssignment, ServiceStatus], safe=True)
