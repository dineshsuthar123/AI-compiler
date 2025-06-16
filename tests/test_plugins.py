import pytest
from pathlib import Path
from typing import Dict, Any

from compiler.plugins import PluginManager
from compiler.plugins.base import (
    BasePlugin,
    PreprocessorPlugin,
    ASTAnalyzerPlugin,
    IROptimizerPlugin
)
from compiler.config import ConfigLoader

class TestPreprocessorPlugin(PreprocessorPlugin):
    """Test preprocessor plugin."""
    
    @property
    def name(self) -> str:
        return "test_preprocessor"
        
    @property
    def description(self) -> str:
        return "Test preprocessor plugin"
        
    def process(self, source_code: str) -> str:
        return source_code.replace("test", "TEST")
        
class TestASTAnalyzerPlugin(ASTAnalyzerPlugin):
    """Test AST analyzer plugin."""
    
    @property
    def name(self) -> str:
        return "test_ast_analyzer"
        
    @property
    def description(self) -> str:
        return "Test AST analyzer plugin"
        
    def analyze(self, ast: Any) -> Any:
        return ast
        
class TestIROptimizerPlugin(IROptimizerPlugin):
    """Test IR optimizer plugin."""
    
    @property
    def name(self) -> str:
        return "test_ir_optimizer"
        
    @property
    def description(self) -> str:
        return "Test IR optimizer plugin"
        
    def optimize(self, ir_module: Any) -> Any:
        return ir_module
        
@pytest.fixture
def plugin_config() -> ConfigLoader:
    """Create a test configuration for plugins."""
    config = ConfigLoader()
    config.set("plugins.enabled", [
        "test_preprocessor",
        "test_ast_analyzer",
        "test_ir_optimizer"
    ])
    return config
    
@pytest.fixture
def plugin_manager(plugin_config: ConfigLoader) -> PluginManager:
    """Create a test plugin manager."""
    manager = PluginManager(plugin_config)
    manager.plugins = {
        "test_preprocessor": TestPreprocessorPlugin(),
        "test_ast_analyzer": TestASTAnalyzerPlugin(),
        "test_ir_optimizer": TestIROptimizerPlugin()
    }
    return manager
    
def test_plugin_loading(plugin_manager: PluginManager):
    """Test plugin loading."""
    assert "test_preprocessor" in plugin_manager.plugins
    assert "test_ast_analyzer" in plugin_manager.plugins
    assert "test_ir_optimizer" in plugin_manager.plugins
    
def test_preprocessor_plugin(plugin_manager: PluginManager):
    """Test preprocessor plugin functionality."""
    source_code = "This is a test string"
    processed = plugin_manager.run_preprocessors(source_code)
    assert processed == "This is a TEST string"
    
def test_ast_analyzer_plugin(plugin_manager: PluginManager):
    """Test AST analyzer plugin functionality."""
    ast = {"type": "test"}
    analyzed = plugin_manager.run_ast_analyzers(ast)
    assert analyzed == ast
    
def test_ir_optimizer_plugin(plugin_manager: PluginManager):
    """Test IR optimizer plugin functionality."""
    ir_module = "test ir module"
    optimized = plugin_manager.run_ir_optimizers(ir_module)
    assert optimized == ir_module
    
def test_plugin_info(plugin_manager: PluginManager):
    """Test getting plugin information."""
    info = plugin_manager.get_plugin_info()
    assert "test_preprocessor" in info
    assert info["test_preprocessor"]["type"] == "TestPreprocessorPlugin"
    
def test_enable_plugin(plugin_manager: PluginManager):
    """Test enabling a plugin."""
    plugin_manager.enable_plugin("test_preprocessor")
    assert plugin_manager.plugins["test_preprocessor"].enabled
    
def test_disable_plugin(plugin_manager: PluginManager):
    """Test disabling a plugin."""
    plugin_manager.disable_plugin("test_preprocessor")
    assert not plugin_manager.plugins["test_preprocessor"].enabled
    
def test_plugin_error_handling(plugin_manager: PluginManager):
    """Test error handling in plugins."""
    # Test with invalid plugin type
    class InvalidPlugin(BasePlugin):
        @property
        def name(self) -> str:
            return "invalid"
            
        @property
        def description(self) -> str:
            return "Invalid plugin"
            
    plugin_manager.plugins["invalid"] = InvalidPlugin()
    
    # These should not raise exceptions
    plugin_manager.run_preprocessors("test")
    plugin_manager.run_ast_analyzers({})
    plugin_manager.run_ir_optimizers("test") 