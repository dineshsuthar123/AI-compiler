from typing import Optional, Dict, Any
import logging
from pathlib import Path
import tempfile
import subprocess

from frontend.parser.c_parser import CParser
from ir.ir_generator import IRGenerator
from ai_module.optimizer import AIOptimizer
from ai_module.feature_extractor import FeatureExtractor

class Compiler:
    """Main AI Compiler class that orchestrates the compilation process."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the compiler with optional configuration.
        
        Args:
            config: Dictionary containing compiler configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Initialize components
        self.parser = CParser()
        self.ir_generator = IRGenerator()
        self.feature_extractor = FeatureExtractor()
        self.ai_optimizer = AIOptimizer()
    
    def _setup_logging(self):
        """Configure logging for the compiler."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def compile(self, source: str, output_file: Optional[str] = None) -> str:
        """Compile the source code using AI-driven optimizations.
        
        Args:
            source: Source code string or path to source file
            output_file: Optional path for the output file
            
        Returns:
            Path to the compiled output file
        """
        self.logger.info("Starting compilation process")
        
        try:
            # Read source code if it's a file path
            if Path(source).exists():
                with open(source, 'r') as f:
                    source_code = f.read()
            else:
                source_code = source
            
            # 1. Parse source code to AST
            self.logger.info("Parsing source code")
            ast = self.parser.parse(source_code)
            
            # 2. Generate LLVM IR
            self.logger.info("Generating LLVM IR")
            ir = self.ir_generator.visit(ast)
            ir_code = self.ir_generator.get_ir()
            
            # 3. Extract features for AI optimization
            self.logger.info("Extracting code features")
            features = self.feature_extractor.extract_features(ir_code)
            
            # 4. Apply AI optimizations
            self.logger.info("Applying AI optimizations")
            optimized_ir = self.ai_optimizer.optimize(ir_code)
            
            # 5. Generate output file
            if output_file is None:
                output_file = tempfile.mktemp(suffix='.o')
            
            # 6. Use LLVM to compile IR to object file
            self.logger.info(f"Generating object file: {output_file}")
            self._compile_ir_to_object(optimized_ir, output_file)
            
            self.logger.info(f"Compilation completed successfully: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Compilation failed: {str(e)}")
            raise
    
    def _compile_ir_to_object(self, ir_code: str, output_file: str):
        """Compile LLVM IR to object file using llc."""
        # Write IR to temporary file
        ir_file = tempfile.mktemp(suffix='.ll')
        with open(ir_file, 'w') as f:
            f.write(ir_code)
        
        # Use llc to compile IR to object file
        try:
            subprocess.run(['llc', '-filetype=obj', ir_file, '-o', output_file], check=True)
        finally:
            # Clean up temporary file
            Path(ir_file).unlink()
    
    @property
    def version(self) -> str:
        """Return the compiler version."""
        return "0.1.0" 