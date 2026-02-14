"""
Pytest configuration and shared fixtures for tests.

Provides common fixtures and test utilities used across test suite.
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyargus import AppConfig, Application, Logger
from pyargus.exceptions import ConfigurationError


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return AppConfig(
        app_name="PyArgus-Test",
        version="0.1.0",
        debug=True,
        environment="test",
        log_level="DEBUG",
    )


@pytest.fixture
def test_logger():
    """Create a test logger."""
    return Logger("PyArgus-Test", "DEBUG")


@pytest.fixture
def test_app(test_config):
    """Create a test application instance."""
    app = Application(test_config)
    app.initialize()
    yield app
    app.shutdown()


@pytest.fixture
def encryption_key():
    """Provide a test encryption key."""
    return "test-encryption-key-32-chars-long!"


@pytest.fixture(autouse=True)
def reset_config():
    """Reset AppConfig singleton before each test."""
    AppConfig.reset_instance()
    yield
    AppConfig.reset_instance()


class TestHelper:
    """Helper utilities for testing."""
    
    @staticmethod
    def create_temp_ssh_key(temp_dir: str) -> Path:
        """Create a temporary SSH key for testing."""
        key_path = Path(temp_dir) / "test_key"
        # Create a dummy key file for testing
        with open(key_path, "w") as f:
            f.write("-----BEGIN RSA PRIVATE KEY-----\n")
            f.write("MIIEowIBAAKCAQEA...\n")
            f.write("-----END RSA PRIVATE KEY-----\n")
        return key_path
    
    @staticmethod
    def create_temp_authorized_keys(temp_dir: str) -> Path:
        """Create a temporary authorized_keys file."""
        keys_path = Path(temp_dir) / "authorized_keys"
        with open(keys_path, "w") as f:
            f.write("")
        return keys_path


@pytest.fixture
def test_helper():
    """Provide test helper utilities."""
    return TestHelper()
