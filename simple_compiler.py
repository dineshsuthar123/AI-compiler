from typing import Optional, Dict, Any
import logging
from pathlib import Path
import json
import yaml
import re
import sys
import subprocess
import tempfile
import os
import tempfile
import subprocess
import sys
import os

from frontend import plugin_manager
from frontend.parser import Parser
from ir.ir_generator import IRGenerator
from ir.ir_formatter import IRFormatter
from ir.ir_executor import IRExecutor

class ModernCompiler:
    """Next-generation compiler with modern features."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the compiler with optional configuration."""
        self.config = self._load_config(config)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Initialize components
        self.parser = Parser()
        self.ir_generator = IRGenerator()
        self.ir_formatter = IRFormatter()
        self.ir_executor = IRExecutor()
        
        # Load plugins
        self._init_plugins()
    
    def _load_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Load configuration from various sources."""
        default_config = {
            'optimization_level': 0,
            'target_arch': 'x86_64',
            'target_os': 'windows',
            'include_paths': [],
            'macros': {},
            'plugins': {
                'enabled': ['preprocessor', 'parser', 'ast'],
                'disabled': [],
                'custom_paths': []
            }
        }
        
        # Load from config file if exists
        config_path = Path('compiler_config.yaml')
        if config_path.exists():
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                default_config.update(file_config)
        
        # Update with provided config
        if config:
            default_config.update(config)
        
        return default_config
    
    def _setup_logging(self):
        """Configure logging for the compiler."""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))
        format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=level,
            format=format
        )
    
    def _init_plugins(self):
        """Initialize and load plugins."""
        plugin_config = self.config['plugins']
        
        # Add custom plugin paths
        for path in plugin_config['custom_paths']:
            plugin_manager.load_plugins(path)
        
        # Load built-in plugins
        plugin_manager.load_plugins()
        
        # Configure plugins
        for plugin_name, plugin in plugin_manager.plugins.items():
            if plugin_name in plugin_config['enabled']:
                plugin.initialize(self.config)
            else:
                self.logger.info(f"Plugin {plugin_name} is disabled")
    
    def compile(self, source: str, execute: bool = True) -> str:
        """Compile the source code to LLVM IR and optionally execute it.
        
        Args:
            source: Source code string or path to source file
            execute: Whether to execute the compiled code
            
        Returns:
            Generated LLVM IR code as string
        """
        self.logger.info("Starting compilation process")
        
        try:
            # Read source code if it's a file path
            if Path(source).exists():
                with open(source, 'r') as f:
                    source_code = f.read()
            else:
                source_code = source
            
            # Process source through plugins
            self.logger.info("Processing source code through plugins")
            processed_code = plugin_manager.process_source(source_code, self.config)
            
            # Parse source code into AST
            self.logger.info("Parsing source code into AST")
            ast = self.parser.parse(processed_code)
            print("\n[DEBUG] AST:", ast)
            
            # Generate LLVM IR
            self.logger.info("Generating LLVM IR")
            self.ir_generator.visit(ast)
            ir_code = str(self.ir_generator.module)
            print("\n[DEBUG] Generated IR:\n", ir_code)
            
            # Check for main function in IR (support both quoted and unquoted)
            main_func_pattern = re.compile(r'define\s+\w+\s+@("main"|main)\s*\(')
            if not main_func_pattern.search(ir_code):
                raise RuntimeError("No 'main' function found in the generated IR. Please ensure your C code contains a valid 'int main()' function.\n[DEBUG] IR:\n" + ir_code)
            
            # Format the IR code
            self.logger.info("Formatting LLVM IR")
            formatted_ir = self.ir_formatter.format_with_comments(ir_code)
            
            # Execute the code if requested
            if execute:
                self.logger.info("Executing compiled code")
                result = self.ir_executor.execute(ir_code)
                print(f"\nProgram output: {result}")
            
            self.logger.info("Compilation completed successfully")
            return formatted_ir
            
        except Exception as e:
            self.logger.error(f"Compilation failed: {str(e)}")
            raise
    
    def generate_ir_only(self, source: str) -> str:
        """Generate LLVM IR without execution.
        
        Args:
            source: Source code string or path to source file
            
        Returns:
            Generated LLVM IR code as string
        """
        try:
            # Read source code if it's a file path
            if Path(source).exists():
                with open(source, 'r') as f:
                    source_code = f.read()
            else:
                source_code = source
            
            # Process source through plugins
            processed_code = plugin_manager.process_source(source_code, self.config)
            
            # Parse source code into AST
            ast = self.parser.parse(processed_code)
            
            # Generate LLVM IR
            self.ir_generator.visit(ast)
            ir_code = str(self.ir_generator.module)
            
            return ir_code
            
        except Exception as e:
            self.logger.error(f"IR generation failed: {str(e)}")
            raise
    
    def compile_to_binary(self, source: str, output_file: str) -> str:
        """Compile source code to binary executable.
        
        Args:
            source: Source code string or path to source file
            output_file: Path for the output binary file
            
        Returns:
            Path to the compiled binary
        """
        try:
            # Generate IR
            ir_code = self.generate_ir_only(source)
            
            # Create temporary IR file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as f:
                f.write(ir_code)
                ir_file = f.name
            
            try:
                # Use llc to compile to object file
                obj_file = ir_file.replace('.ll', '.o')
                llc_cmd = ['llc', '-filetype=obj', ir_file, '-o', obj_file]
                
                # Try to run llc
                result = subprocess.run(llc_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    # Fallback: save as IR file
                    import shutil
                    shutil.copy(ir_file, output_file.replace('.exe', '.ll').replace('.out', '.ll'))
                    return output_file.replace('.exe', '.ll').replace('.out', '.ll')
                
                # Link to executable
                if sys.platform == 'win32':
                    link_cmd = ['gcc', obj_file, '-o', output_file]
                else:
                    link_cmd = ['gcc', obj_file, '-o', output_file]
                
                result = subprocess.run(link_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    # Fallback: return object file
                    return obj_file
                
                return output_file
                
            finally:
                # Cleanup
                try:
                    os.unlink(ir_file)
                except:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Binary compilation failed: {str(e)}")
            # Return IR as fallback
            ir_code = self.generate_ir_only(source)
            with open(output_file.replace('.exe', '.ll').replace('.out', '.ll'), 'w') as f:
                f.write(ir_code)
            return output_file.replace('.exe', '.ll').replace('.out', '.ll')

    def get_plugin(self, name: str):
        """Get a plugin by name."""
        return plugin_manager.get_plugin(name)
    
    @property
    def version(self) -> str:
        """Return the compiler version."""
        return "1.0.0"
    
    def save_config(self, path: Optional[str] = None):
        """Save the current configuration to a file."""
        if path is None:
            path = 'compiler_config.yaml'
        
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def load_config(self, path: str):
        """Load configuration from a file."""
        with open(path, 'r') as f:
            self.config = yaml.safe_load(f)
        self._init_plugins()