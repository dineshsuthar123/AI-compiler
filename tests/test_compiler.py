import unittest
from frontend.parser.c_parser import CParser
from ir.ir_generator import IRGenerator
from frontend.ast.nodes import *
import pytest
from pathlib import Path
from typing import Dict, Any

from compiler.core import Compiler
from compiler.config import ConfigLoader
from compiler.exceptions import CompilerError

class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.parser = CParser()
        self.ir_generator = IRGenerator()
    
    def test_simple_function(self):
        # Test a simple function that adds two numbers
        source = """
        int add(int a, int b) {
            return a + b;
        }
        """
        
        # Parse the source code
        ast = self.parser.parse(source)
        
        # Verify AST structure
        self.assertIsInstance(ast, TranslationUnit)
        self.assertEqual(len(ast.declarations), 1)
        
        func = ast.declarations[0]
        self.assertIsInstance(func, FunctionDecl)
        self.assertEqual(func.name, "add")
        self.assertEqual(len(func.parameters), 2)
        self.assertEqual(func.parameters[0].name, "a")
        self.assertEqual(func.parameters[1].name, "b")
        
        # Generate IR
        self.ir_generator.visit(ast)
        ir_code = str(self.ir_generator.module)
        
        # Verify IR code contains essential parts
        self.assertIn("define i32 @add(i32 %a, i32 %b)", ir_code)
        self.assertIn("add i32 %a, %b", ir_code)
    
    def test_if_statement(self):
        # Test a function with an if statement
        source = """
        int max(int a, int b) {
            if (a > b) {
                return a;
            } else {
                return b;
            }
        }
        """
        
        # Parse and generate IR
        ast = self.parser.parse(source)
        self.ir_generator.visit(ast)
        ir_code = str(self.ir_generator.module)
        
        # Verify IR code contains branching
        self.assertIn("icmp sgt i32 %a, %b", ir_code)  # signed greater than
        self.assertIn("br i1", ir_code)  # conditional branch
    
    def test_while_loop(self):
        # Test a function with a while loop
        source = """
        int factorial(int n) {
            int result = 1;
            while (n > 0) {
                result = result * n;
                n = n - 1;
            }
            return result;
        }
        """
        
        # Parse and generate IR
        ast = self.parser.parse(source)
        self.ir_generator.visit(ast)
        ir_code = str(self.ir_generator.module)
        
        # Verify IR code contains loop structure
        self.assertIn("while.cond", ir_code)
        self.assertIn("while.body", ir_code)
        self.assertIn("while.end", ir_code)
    
    def test_multiple_functions(self):
        # Test multiple function definitions
        source = """
        int add(int a, int b) {
            return a + b;
        }
        
        int sub(int a, int b) {
            return a - b;
        }
        """
        
        # Parse and verify AST
        ast = self.parser.parse(source)
        self.assertEqual(len(ast.declarations), 2)
        
        # Generate and verify IR
        self.ir_generator.visit(ast)
        ir_code = str(self.ir_generator.module)
        
        self.assertIn("define i32 @add(i32 %a, i32 %b)", ir_code)
        self.assertIn("define i32 @sub(i32 %a, i32 %b)", ir_code)
    
    def test_pointer_types(self):
        # Test function with pointer parameters
        source = """
        int sum_array(int* arr, int size) {
            int sum = 0;
            int i = 0;
            while (i < size) {
                sum = sum + arr[i];
                i = i + 1;
            }
            return sum;
        }
        """
        
        # Parse and verify AST
        ast = self.parser.parse(source)
        func = ast.declarations[0]
        
        self.assertTrue(func.parameters[0].type.is_pointer)
        self.assertEqual(func.parameters[0].type.name, "int")
        
        # Generate IR
        self.ir_generator.visit(ast)
        ir_code = str(self.ir_generator.module)
        
        # Verify IR code handles pointers
        self.assertIn("i32*", ir_code)  # pointer type
        self.assertIn("load i32, i32*", ir_code)  # pointer dereferencing

@pytest.fixture
def config() -> ConfigLoader:
    """Create a test configuration."""
    return ConfigLoader()

@pytest.fixture
def compiler(config: ConfigLoader) -> Compiler:
    """Create a test compiler instance."""
    return Compiler(config)

def test_compile_simple(compiler: Compiler, tmp_path: Path) -> None:
    """Test compiling a simple C program."""
    source = tmp_path / "test.c"
    source.write_text("""
    int main() {
        return 0;
    }
    """)
    
    result = compiler.compile(source)
    assert result["success"]
    assert Path(result["output_path"]).exists()
    
def test_compile_with_ai(compiler: Compiler, tmp_path: Path) -> None:
    """Test compiling with AI analysis enabled."""
    # Enable AI features
    compiler.config.set("ai.enabled", True)
    compiler.config.set("ai.features.code_analysis", True)
    
    source = tmp_path / "test.c"
    source.write_text("""
    int main() {
        int x = 0;
        for (int i = 0; i < 10; i++) {
            x += i;
        }
        return x;
    }
    """)
    
    result = compiler.compile(source)
    assert result["success"]
    assert "ai_analysis" in result
    
def test_compile_with_plugins(compiler: Compiler, tmp_path: Path) -> None:
    """Test compiling with plugins enabled."""
    # Enable some plugins
    compiler.config.set("plugins.enabled", ["preprocessor", "optimizer"])
    
    source = tmp_path / "test.c"
    source.write_text("""
    #define VALUE 42
    
    int main() {
        return VALUE;
    }
    """)
    
    result = compiler.compile(source)
    assert result["success"]
    
def test_compile_error(compiler: Compiler, tmp_path: Path) -> None:
    """Test handling compilation errors."""
    source = tmp_path / "test.c"
    source.write_text("""
    int main() {
        return x;  // Undefined variable
    }
    """)
    
    with pytest.raises(CompilerError):
        compiler.compile(source)
        
def test_config_management(compiler: Compiler) -> None:
    """Test configuration management."""
    # Get current config
    config = compiler.get_config()
    assert "core" in config
    assert "compilation" in config
    
    # Update config
    updates = {
        "compilation.optimization_level": 3,
        "ai.enabled": True
    }
    compiler.update_config(updates)
    
    # Verify updates
    new_config = compiler.get_config()
    assert new_config["compilation"]["optimization_level"] == 3
    assert new_config["ai"]["enabled"] is True
    
def test_plugin_management(compiler: Compiler) -> None:
    """Test plugin management."""
    # Get available plugins
    plugins = compiler.get_available_plugins()
    assert isinstance(plugins, dict)
    
    # Enable a plugin
    if "preprocessor" in plugins:
        compiler.plugin_manager.enable_plugin("preprocessor")
        assert compiler.plugin_manager.plugins["preprocessor"].enabled
        
    # Disable a plugin
    if "preprocessor" in plugins:
        compiler.plugin_manager.disable_plugin("preprocessor")
        assert not compiler.plugin_manager.plugins["preprocessor"].enabled

if __name__ == '__main__':
    unittest.main() 