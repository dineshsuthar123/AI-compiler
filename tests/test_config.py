import pytest
from pathlib import Path
import yaml
from typing import Dict, Any

from compiler.config import ConfigLoader
from compiler.exceptions import CompilerError

@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Create a test configuration file."""
    config_path = tmp_path / "test_config.yaml"
    config = {
        "core": {
            "version": "1.0.0",
            "debug": True
        },
        "compilation": {
            "optimization_level": 3
        }
    }
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config_path
    
@pytest.fixture
def config(config_file: Path) -> ConfigLoader:
    """Create a test configuration loader."""
    return ConfigLoader(str(config_file))
    
def test_load_config(config: ConfigLoader):
    """Test loading configuration from file."""
    assert config.get("core.version") == "1.0.0"
    assert config.get("core.debug") is True
    assert config.get("compilation.optimization_level") == 3
    
def test_get_nonexistent_key(config: ConfigLoader):
    """Test getting nonexistent configuration keys."""
    assert config.get("nonexistent.key") is None
    assert config.get("nonexistent.key", "default") == "default"
    
def test_set_config(config: ConfigLoader):
    """Test setting configuration values."""
    config.set("core.version", "2.0.0")
    assert config.get("core.version") == "2.0.0"
    
    config.set("new.section.value", 42)
    assert config.get("new.section.value") == 42
    
def test_save_config(config: ConfigLoader, config_file: Path):
    """Test saving configuration to file."""
    config.set("core.version", "2.0.0")
    config.save()
    
    with open(config_file) as f:
        saved_config = yaml.safe_load(f)
    assert saved_config["core"]["version"] == "2.0.0"
    
def test_validate_config(config: ConfigLoader):
    """Test configuration validation."""
    assert config.validate()
    
    # Remove required section
    config.config.pop("core")
    assert not config.validate()
    
def test_get_section_config(config: ConfigLoader):
    """Test getting section configurations."""
    core_config = config.get_core_config()
    assert core_config["version"] == "1.0.0"
    assert core_config["debug"] is True
    
    compilation_config = config.get_compilation_config()
    assert compilation_config["optimization_level"] == 3
    
def test_get_all_config(config: ConfigLoader):
    """Test getting all configuration."""
    all_config = config.get_all()
    assert "core" in all_config
    assert "compilation" in all_config
    
def test_invalid_config_file(tmp_path: Path):
    """Test handling invalid configuration file."""
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("invalid: yaml: content")
    
    with pytest.raises(ValueError):
        ConfigLoader(str(invalid_file))
        
def test_nonexistent_config_file(tmp_path: Path):
    """Test handling nonexistent configuration file."""
    with pytest.raises(FileNotFoundError):
        ConfigLoader(str(tmp_path / "nonexistent.yaml"))
        
def test_default_config():
    """Test using default configuration."""
    config = ConfigLoader()
    assert config.get("core.version") is None
    assert config.get("core.version", "1.0.0") == "1.0.0" 