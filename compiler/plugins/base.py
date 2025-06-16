from abc import ABC, abstractmethod
from typing import Any, Dict

from compiler.config import ConfigLoader

class BasePlugin(ABC):
    """Base class for all compiler plugins."""
    
    def __init__(self):
        """Initialize the plugin."""
        self.enabled = False
        self.config: ConfigLoader = None
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the plugin."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the description of the plugin."""
        pass
        
    def initialize(self, config: ConfigLoader) -> None:
        """Initialize the plugin with configuration."""
        self.config = config
        self.enabled = True
        
    def get_config(self) -> Dict[str, Any]:
        """Get the plugin's configuration."""
        return self.config.get(f"plugins.{self.name}", {})
        
class PreprocessorPlugin(BasePlugin):
    """Base class for preprocessor plugins."""
    
    @abstractmethod
    def process(self, source_code: str) -> str:
        """Process the source code before parsing.
        
        Args:
            source_code: The source code to process
            
        Returns:
            The processed source code
        """
        pass
        
class ASTAnalyzerPlugin(BasePlugin):
    """Base class for AST analyzer plugins."""
    
    @abstractmethod
    def analyze(self, ast: Any) -> Any:
        """Analyze and potentially modify the AST.
        
        Args:
            ast: The abstract syntax tree to analyze
            
        Returns:
            The potentially modified AST
        """
        pass
        
class IROptimizerPlugin(BasePlugin):
    """Base class for IR optimizer plugins."""
    
    @abstractmethod
    def optimize(self, ir_module: Any) -> Any:
        """Optimize the LLVM IR module.
        
        Args:
            ir_module: The LLVM IR module to optimize
            
        Returns:
            The optimized IR module
        """
        pass 