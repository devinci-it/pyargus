"""
PyArgus Data Directory Management.

Handles centralized storage of app data (logs, databases, cache, etc.)
following XDG Base Directory specification.

Usage:
    from pyargus.core.paths import get_app_data_dir, get_logs_dir
    
    logs_dir = get_logs_dir()
    db_path = get_app_data_dir() / "pyargus.db"
"""

import os
from pathlib import Path
from typing import Optional


def get_app_data_dir(app_name: str = "pyargus") -> Path:
    """
    Get centralized application data directory.
    
    Priority:
    1. PYARGUS_DATA_DIR environment variable (if set)
    2. $XDG_DATA_HOME/pyargus/ (Linux/Unix standard)
    3. ~/.local/share/pyargus/ (Linux/Unix default)
    4. ~/AppData/pyargus/ (Windows)
    5. ~/.pyargus/ (fallback)
    
    Args:
        app_name: Application name for directory
        
    Returns:
        Path: Application data directory (created if doesn't exist)
    """
    # Check explicit override
    if override := os.getenv('PYARGUS_DATA_DIR'):
        app_dir = Path(override).expanduser().resolve()
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
    
    # Use XDG Base Directory standard
    if xdg_data := os.getenv('XDG_DATA_HOME'):
        app_dir = Path(xdg_data) / app_name
    elif os.name == 'nt':  # Windows
        app_dir = Path.home() / 'AppData' / app_name
    else:  # Unix/Linux default
        app_dir = Path.home() / '.local' / 'share' / app_name
    
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_logs_dir(app_name: str = "pyargus") -> Path:
    """
    Get application logs directory.
    
    Priority:
    1. PYARGUS_LOGS_DIR environment variable (if set)
    2. $XDG_STATE_HOME/pyargus/logs/ (Linux standard)
    3. $PYARGUS_DATA_DIR/logs/
    4. ~/.local/state/pyargus/logs/ (Linux/Unix default)
    5. ~/.pyargus/logs/ (fallback)
    
    Args:
        app_name: Application name for directory
        
    Returns:
        Path: Logs directory (created if doesn't exist)
    """
    # Check explicit override
    if override := os.getenv('PYARGUS_LOGS_DIR'):
        logs_dir = Path(override).expanduser().resolve()
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir
    
    # Use XDG spec for state/logs
    if xdg_state := os.getenv('XDG_STATE_HOME'):
        logs_dir = Path(xdg_state) / app_name / 'logs'
    else:
        # Fall back to data directory
        data_dir = get_app_data_dir(app_name)
        logs_dir = data_dir / 'logs'
    
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_cache_dir(app_name: str = "pyargus") -> Path:
    """
    Get application cache directory.
    
    Priority:
    1. PYARGUS_CACHE_DIR environment variable
    2. $XDG_CACHE_HOME/pyargus/
    3. ~/.cache/pyargus/ (Linux/Unix default)
    4. ~/AppData/Local/Temp/pyargus/ (Windows)
    
    Args:
        app_name: Application name for directory
        
    Returns:
        Path: Cache directory (created if doesn't exist)
    """
    # Check explicit override
    if override := os.getenv('PYARGUS_CACHE_DIR'):
        cache_dir = Path(override).expanduser().resolve()
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    if xdg_cache := os.getenv('XDG_CACHE_HOME'):
        cache_dir = Path(xdg_cache) / app_name
    elif os.name == 'nt':  # Windows
        cache_dir = Path.home() / 'AppData' / 'Local' / 'Temp' / app_name
    else:  # Unix/Linux default
        cache_dir = Path.home() / '.cache' / app_name
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_config_dir(app_name: str = "pyargus") -> Path:
    """
    Get application configuration directory.
    
    Priority:
    1. PYARGUS_CONFIG_DIR environment variable
    2. $XDG_CONFIG_HOME/pyargus/
    3. ~/.config/pyargus/ (Linux/Unix default)
    4. ~/AppData/pyargus/ (Windows)
    
    Args:
        app_name: Application name for directory
        
    Returns:
        Path: Config directory (created if doesn't exist)
    """
    # Check explicit override
    if override := os.getenv('PYARGUS_CONFIG_DIR'):
        config_dir = Path(override).expanduser().resolve()
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    if xdg_config := os.getenv('XDG_CONFIG_HOME'):
        config_dir = Path(xdg_config) / app_name
    elif os.name == 'nt':  # Windows
        config_dir = Path.home() / 'AppData' / app_name
    else:  # Unix/Linux default
        config_dir = Path.home() / '.config' / app_name
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


__all__ = [
    "get_app_data_dir",
    "get_logs_dir",
    "get_cache_dir",
    "get_config_dir",
]
