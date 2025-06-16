from pathlib import Path
from typing import Optional, Dict, Any

from compiler.config import ConfigLoader
from compiler.exceptions import CompilerError
from compiler.frontend import Frontend
from compiler.ir import IRGenerator
from compiler.plugins import PluginManager
from compiler.ai import AIAnalyzer

class Compiler:
    """Main compiler class that orchestrates the compilation process."""
    
    def __init__(self, config: ConfigLoader):
        """Initialize the compiler with configuration."""
        self.config = config
        self.frontend = Frontend(config)
        self.ir_generator = IRGenerator(config)
        self.plugin_manager = PluginManager(config)
        self.ai_analyzer = AIAnalyzer(config) if config.get("ai.enabled") else None
        
        # Load and initialize plugins
        self.plugin_manager.load_plugins()
        
    def compile(
        self,
        source_path: Path,
        output_path: Optional[Path] = None,
        optimization_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """Compile source code to LLVM IR.
        
        Args:
            source_path: Path to the source file
            output_path: Path to write the output to (default: source_path with .ll extension)
            optimization_level: Override the optimization level from config
            
        Returns:
            Dictionary containing compilation results and metadata
        """
        if not source_path.exists():
            raise CompilerError(f"Source file {source_path} does not exist")
            
        if output_path is None:
            output_path = source_path.with_suffix(".ll")
            
        # Read source code
        with open(source_path, "r") as f:
            source_code = f.read()
            
        # Run preprocessor plugins
        source_code = self.plugin_manager.run_preprocessors(source_code)
        
        # Parse source code
        try:
            ast = self.frontend.parse(source_code)
        except Exception as e:
            raise CompilerError(f"Parsing failed: {str(e)}")
            
        # Run AST analysis plugins
        ast = self.plugin_manager.run_ast_analyzers(ast)
        
        # AI analysis if enabled
        if self.ai_analyzer:
            ai_analysis = self.ai_analyzer.analyze(ast, source_code)
            if ai_analysis.get("suggestions"):
                print("AI Analysis Suggestions:")
                for suggestion in ai_analysis["suggestions"]:
                    print(f"- {suggestion}")
                    
        # Generate IR
        try:
            ir_module = self.ir_generator.generate(ast)
        except Exception as e:
            raise CompilerError(f"IR generation failed: {str(e)}")
            
        # Run IR optimization plugins
        ir_module = self.plugin_manager.run_ir_optimizers(ir_module)
        
        # Write output
        try:
            with open(output_path, "w") as f:
                f.write(str(ir_module))
        except Exception as e:
            raise CompilerError(f"Failed to write output: {str(e)}")
            
        return {
            "success": True,
            "source_path": str(source_path),
            "output_path": str(output_path),
            "optimization_level": optimization_level or self.config.get("compilation.optimization_level"),
            "ai_analysis": ai_analysis if self.ai_analyzer else None
        }
        
    def get_available_plugins(self) -> Dict[str, Any]:
        """Get information about available plugins."""
        return self.plugin_manager.get_plugin_info()
        
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self.config.get_all()
        
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update the configuration."""
        for key, value in updates.items():
            self.config.set(key, value)
        self.config.save() 