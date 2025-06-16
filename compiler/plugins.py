import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List, Type, Optional

from compiler.config import ConfigLoader
from compiler.exceptions import CompilerError
from compiler.plugins.base import (
    PreprocessorPlugin,
    ASTAnalyzerPlugin,
    IROptimizerPlugin,
    BasePlugin
)

class PluginManager:
    """Manages the loading and execution of compiler plugins."""
    
    def __init__(self, config: ConfigLoader):
        """Initialize the plugin manager."""
        self.config = config
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_types = {
            "preprocessor": PreprocessorPlugin,
            "ast_analyzer": ASTAnalyzerPlugin,
            "ir_optimizer": IROptimizerPlugin
        }
        
    def load_plugins(self) -> None:
        """Load all enabled plugins from the configuration."""
        enabled_plugins = self.config.get("plugins.enabled", [])
        custom_paths = self.config.get("plugins.custom_paths", [])
        
        # Load plugins from custom paths
        for path in custom_paths:
            self._load_plugins_from_path(Path(path))
            
        # Load built-in plugins
        self._load_builtin_plugins()
        
        # Initialize enabled plugins
        for plugin_name in enabled_plugins:
            if plugin_name in self.plugins:
                self.plugins[plugin_name].initialize(self.config)
                
    def _load_plugins_from_path(self, path: Path) -> None:
        """Load plugins from a custom path."""
        if not path.exists():
            return
            
        if path.is_file() and path.suffix == ".py":
            self._load_plugin_from_file(path)
        elif path.is_dir():
            for file in path.glob("**/*.py"):
                self._load_plugin_from_file(file)
                
    def _load_plugin_from_file(self, file_path: Path) -> None:
        """Load a plugin from a Python file."""
        try:
            spec = importlib.util.spec_from_file_location(
                file_path.stem, str(file_path)
            )
            if spec is None or spec.loader is None:
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BasePlugin)
                    and obj != BasePlugin
                ):
                    plugin = obj()
                    self.plugins[plugin.name] = plugin
                    
        except Exception as e:
            print(f"Warning: Failed to load plugin from {file_path}: {e}")
            
    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins from the plugins directory."""
        builtin_path = Path(__file__).parent / "plugins"
        if builtin_path.exists():
            self._load_plugins_from_path(builtin_path)
            
    def run_preprocessors(self, source_code: str) -> str:
        """Run all enabled preprocessor plugins."""
        for plugin in self._get_plugins_of_type(PreprocessorPlugin):
            try:
                source_code = plugin.process(source_code)
            except Exception as e:
                print(f"Warning: Preprocessor {plugin.name} failed: {e}")
        return source_code
        
    def run_ast_analyzers(self, ast: Any) -> Any:
        """Run all enabled AST analyzer plugins."""
        for plugin in self._get_plugins_of_type(ASTAnalyzerPlugin):
            try:
                ast = plugin.analyze(ast)
            except Exception as e:
                print(f"Warning: AST analyzer {plugin.name} failed: {e}")
        return ast
        
    def run_ir_optimizers(self, ir_module: Any) -> Any:
        """Run all enabled IR optimizer plugins."""
        for plugin in self._get_plugins_of_type(IROptimizerPlugin):
            try:
                ir_module = plugin.optimize(ir_module)
            except Exception as e:
                print(f"Warning: IR optimizer {plugin.name} failed: {e}")
        return ir_module
        
    def _get_plugins_of_type(self, plugin_type: Type[BasePlugin]) -> List[BasePlugin]:
        """Get all enabled plugins of a specific type."""
        return [
            plugin for plugin in self.plugins.values()
            if isinstance(plugin, plugin_type) and plugin.enabled
        ]
        
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get information about all loaded plugins."""
        return {
            name: {
                "type": type(plugin).__name__,
                "enabled": plugin.enabled,
                "description": plugin.description
            }
            for name, plugin in self.plugins.items()
        }
        
    def enable_plugin(self, plugin_name: str) -> None:
        """Enable a specific plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self.config.set(f"plugins.enabled.{plugin_name}", True)
            self.config.save()
            
    def disable_plugin(self, plugin_name: str) -> None:
        """Disable a specific plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            self.config.set(f"plugins.enabled.{plugin_name}", False)
            self.config.save() 