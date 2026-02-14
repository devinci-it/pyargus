"""Unit tests for application configuration."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyargus import AppConfig, DatabaseConfig, APIConfig, SecurityConfig
from pyargus.exceptions import ConfigurationError, ValidationError


class TestDatabaseConfig:
    """Tests for DatabaseConfig."""
    
    @pytest.mark.unit
    def test_database_config_creation(self):
        """Test creating database configuration."""
        config = DatabaseConfig(database_url="sqlite:///test.db")
        assert config.database_url == "sqlite:///test.db"
        assert config.echo is False
    
    @pytest.mark.unit
    def test_database_config_validation(self):
        """Test database config validates URL."""
        with pytest.raises(ValueError):
            DatabaseConfig(database_url="")


class TestAPIConfig:
    """Tests for APIConfig."""
    
    @pytest.mark.unit
    def test_api_config_defaults(self):
        """Test API config default values."""
        config = APIConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.debug is False
    
    @pytest.mark.unit
    def test_api_config_invalid_port(self):
        """Test API config validates port range."""
        with pytest.raises(ValueError):
            APIConfig(port=99999)


class TestSecurityConfig:
    """Tests for SecurityConfig."""
    
    @pytest.mark.unit
    def test_security_config_creation(self):
        """Test creating security configuration."""
        config = SecurityConfig(
            encryption_key="test-key",
            ssh_key_path="/path/to/key"
        )
        assert config.encryption_key == "test-key"
        assert config.ssh_key_path == "/path/to/key"
    
    @pytest.mark.unit
    def test_security_config_missing_encryption_key(self):
        """Test security config requires encryption key."""
        with pytest.raises(ValueError):
            SecurityConfig(
                encryption_key="",
                ssh_key_path="/path/to/key"
            )
    
    @pytest.mark.unit
    def test_security_config_missing_ssh_key_path(self):
        """Test security config requires SSH key path."""
        with pytest.raises(ValueError):
            SecurityConfig(
                encryption_key="test-key",
                ssh_key_path=""
            )


class TestAppConfig:
    """Tests for AppConfig (Singleton)."""
    
    @pytest.mark.unit
    def test_app_config_singleton(self, test_config):
        """Test AppConfig singleton pattern."""
        instance1 = AppConfig.get_instance(app_name="Test1")
        instance2 = AppConfig.get_instance()
        
        assert instance1 is instance2
        assert instance1.app_name == "Test1"
    
    @pytest.mark.unit
    def test_app_config_reset(self):
        """Test AppConfig can be reset."""
        instance1 = AppConfig.get_instance(app_name="Test1")
        AppConfig.reset_instance()
        instance2 = AppConfig.get_instance(app_name="Test2")
        
        assert instance1 is not instance2
        assert instance2.app_name == "Test2"
    
    @pytest.mark.unit
    def test_app_config_from_env(self, monkeypatch):
        """Test loading AppConfig from environment."""
        monkeypatch.setenv("APP_NAME", "EnvTest")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("API_PORT", "9000")
        monkeypatch.setenv("ENCRYPTION_KEY", "test-key")
        monkeypatch.setenv("SSH_KEY_PATH", "/path/to/key")
        
        AppConfig.reset_instance()
        config = AppConfig.from_env()
        
        assert config.app_name == "EnvTest"
        assert config.debug is True
        assert config.api.port == 9000
