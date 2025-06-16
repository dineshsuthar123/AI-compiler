"""Frontend package for C to LLVM IR compiler."""

from .parser.c_parser import CParser
from .ast.nodes import *
from typing import Dict, Type, Optional, List
from abc import ABC, abstractmethod
from pathlib import Path
import importlib
import pkgutil
import logging

class FrontendPlugin(ABC):
    """Base class for frontend plugins."""
    
    @abstractmethod
    def initialize(self, config: Dict) -> None:
        """Initialize the plugin with configuration."""
        pass
    
    @abstractmethod
    def process(self, source: str) -> str:
        """Process the source code."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the plugin name."""
        pass

class PluginManager:
    """Manages frontend plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, FrontendPlugin] = {}
        self.logger = logging.getLogger(__name__)
    
    def load_plugins(self, plugin_path: Optional[str] = None) -> None:
        """Load plugins from the specified path or default location."""
        if plugin_path is None:
            plugin_path = str(Path(__file__).parent / "plugins")
        
        # Load built-in plugins
        self._load_builtin_plugins()
        
        # Load external plugins
        self._load_external_plugins(plugin_path)
    
    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        builtin_plugins = [
            "preprocessor",
            "parser",
            "ast",
        ]
        
        for plugin_name in builtin_plugins:
            try:
                module = importlib.import_module(f"frontend.{plugin_name}")
                if hasattr(module, "Plugin"):
                    plugin_class = getattr(module, "Plugin")
                    if isinstance(plugin_class, type) and issubclass(plugin_class, FrontendPlugin):
                        plugin_instance = plugin_class()
                        self.register_plugin(plugin_instance)
            except ImportError as e:
                self.logger.warning(f"Failed to load built-in plugin {plugin_name}: {e}")
    
    def _load_external_plugins(self, plugin_path: str) -> None:
        """Load external plugins from the specified path."""
        try:
            for finder, name, _ in pkgutil.iter_modules([plugin_path]):
                try:
                    module = finder.find_module(name).load_module(name)
                    if hasattr(module, "Plugin"):
                        plugin_class = getattr(module, "Plugin")
                        if isinstance(plugin_class, type) and issubclass(plugin_class, FrontendPlugin):
                            plugin_instance = plugin_class()
                            self.register_plugin(plugin_instance)
                except Exception as e:
                    self.logger.warning(f"Failed to load plugin {name}: {e}")
        except Exception as e:
            self.logger.warning(f"Failed to load plugins from {plugin_path}: {e}")
    
    def register_plugin(self, plugin: FrontendPlugin) -> None:
        """Register a new plugin."""
        name = plugin.get_name()
        if name in self.plugins:
            self.logger.warning(f"Plugin {name} already registered, overwriting")
        self.plugins[name] = plugin
        self.logger.info(f"Registered plugin: {name}")
    
    def get_plugin(self, name: str) -> Optional[FrontendPlugin]:
        """Get a plugin by name."""
        return self.plugins.get(name)
    
    def process_source(self, source: str, config: Dict) -> str:
        """Process source code through all registered plugins."""
        processed = source
        for plugin in self.plugins.values():
            try:
                plugin.initialize(config)
                processed = plugin.process(processed)
            except Exception as e:
                self.logger.error(f"Plugin {plugin.get_name()} failed: {e}")
                raise
        return processed

# Create a global plugin manager instance
plugin_manager = PluginManager()

__all__ = ['CParser'] + [cls.__name__ for cls in Node.__subclasses__()] 