import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigLoader:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "..", "compiler_config.yaml")
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def save(self) -> None:
        """Save configuration to YAML file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            raise IOError(f"Error saving configuration: {str(e)}")

    def validate(self) -> bool:
        """Validate the configuration."""
        required_sections = ['core', 'compilation', 'ai', 'plugins', 'web', 'chatbot']
        for section in required_sections:
            if section not in self.config:
                return False
        return True

    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get configuration for a specific plugin."""
        return self.get(f"plugins.{plugin_name}", {})

    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI-related configuration."""
        return self.get("ai", {})

    def get_compilation_config(self) -> Dict[str, Any]:
        """Get compilation-related configuration."""
        return self.get("compilation", {})

    def get_web_config(self) -> Dict[str, Any]:
        """Get web interface configuration."""
        return self.get("web", {})

    def get_chatbot_config(self) -> Dict[str, Any]:
        """Get chatbot configuration."""
        return self.get("chatbot", {}) 