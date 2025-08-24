from typing import Optional, Dict, Any
import logging
from pathlib import Path
import re

from frontend import plugin_manager
from frontend.parser import Parser
from frontend.preprocessor.preprocessor import Preprocessor
from ir.ir_generator import IRGenerator
from ir.ir_formatter import IRFormatter
from ir.ir_executor import IRExecutor

class ModernCompiler:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.preprocessor = Preprocessor(include_paths=self.config.get('include_paths', []))
        self.parser = Parser()
        self.ir_generator = IRGenerator()
        self.ir_formatter = IRFormatter()
        self.ir_executor = IRExecutor()

        # init plugins
        plugin_manager.load_plugins()

    def compile(self, source: str, execute: bool = False) -> str:
        # Read source
        if Path(source).exists():
            code = Path(source).read_text()
        else:
            code = source

        # Preprocess
        code = self.preprocessor.process(code)
        # Plugins
        code = plugin_manager.process_source(code, self.config)
        # Parse
        ast = self.parser.parse(code)
        # IR
        self.ir_generator = IRGenerator()  # fresh module per compile
        self.ir_generator.visit(ast)
        ir_code = str(self.ir_generator.module)

        # Ensure main exists
        if not re.search(r'define\s+\w+\s+@("main"|main)\s*\(', ir_code):
            raise RuntimeError("No 'main' function found in the generated IR.")

        # Format
        formatted = self.ir_formatter.format_with_comments(ir_code)

        if execute:
            exit_code, stdout = self.ir_executor.execute(ir_code)
            self.logger.info("Program output: %s", stdout)
        return formatted

    def generate_ir_only(self, source: str) -> str:
        """Generate IR without executing the program."""
        return self.compile(source, execute=False)

    def compile_and_execute(self, source: str, optimization_level: int = 0, ai_enhanced: bool = False, stdin: str | bytes | None = None) -> Dict[str, Any]:
        ir_code = self.compile(source, execute=False)
        exit_code, stdout = self.ir_executor.execute(str(self.ir_generator.module), stdin_data=stdin)
        return {
            'success': True,
            'ir_code': ir_code,
            'output': stdout,
            'exit_code': exit_code,
            'optimization_level': optimization_level,
            'ai_enhanced': ai_enhanced,
            'compilation_time': 0.0,
            'errors': []
        }
