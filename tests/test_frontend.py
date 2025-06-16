import pytest
from pathlib import Path
from typing import Dict, Any

from compiler.frontend import Parser, ASTBuilder, Preprocessor
from compiler.config import ConfigLoader
from compiler.exceptions import ParsingError

@pytest.fixture
def frontend_config() -> ConfigLoader:
    """Create a test configuration for frontend components."""
    config = ConfigLoader()
    config.set("frontend.preprocessor.macros", {
        "TEST": "42",
        "DEBUG": "1"
    })
    return config

@pytest.fixture
def parser(frontend_config: ConfigLoader) -> Parser:
    """Create a test parser."""
    return Parser(frontend_config)

@pytest.fixture
def ast_builder(frontend_config: ConfigLoader) -> ASTBuilder:
    """Create a test AST builder."""
    return ASTBuilder(frontend_config)

@pytest.fixture
def preprocessor(frontend_config: ConfigLoader) -> Preprocessor:
    """Create a test preprocessor."""
    return Preprocessor(frontend_config)

def test_parse_simple_program(parser: Parser):
    """Test parsing a simple C program."""
    source = """
    int main() {
        return 0;
    }
    """
    ast = parser.parse(source)
    assert ast is not None
    assert ast.type == "program"
    assert len(ast.children) == 1  # main function

def test_parse_complex_program(parser: Parser):
    """Test parsing a more complex C program."""
    source = """
    int add(int a, int b) {
        return a + b;
    }
    
    int main() {
        int x = add(1, 2);
        return x;
    }
    """
    ast = parser.parse(source)
    assert ast is not None
    assert ast.type == "program"
    assert len(ast.children) == 2  # add function and main function

def test_parse_error(parser: Parser):
    """Test handling parsing errors."""
    source = """
    int main() {
        return x;  // Undefined variable
    }
    """
    with pytest.raises(ParsingError):
        parser.parse(source)

def test_build_ast_simple(ast_builder: ASTBuilder):
    """Test building AST for a simple program."""
    source = """
    int main() {
        return 0;
    }
    """
    ast = ast_builder.build(source)
    assert ast is not None
    assert ast.type == "program"
    assert len(ast.children) == 1

def test_build_ast_complex(ast_builder: ASTBuilder):
    """Test building AST for a complex program."""
    source = """
    int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
    
    int main() {
        return factorial(5);
    }
    """
    ast = ast_builder.build(source)
    assert ast is not None
    assert ast.type == "program"
    assert len(ast.children) == 2

def test_preprocess_simple(preprocessor: Preprocessor):
    """Test preprocessing a simple program."""
    source = """
    #define VALUE 42
    int main() {
        return VALUE;
    }
    """
    processed = preprocessor.process(source)
    assert "VALUE" not in processed
    assert "42" in processed

def test_preprocess_complex(preprocessor: Preprocessor):
    """Test preprocessing a complex program."""
    source = """
    #define SQUARE(x) ((x) * (x))
    #define MAX(a, b) ((a) > (b) ? (a) : (b))
    
    int main() {
        int x = SQUARE(5);
        int y = MAX(x, 10);
        return y;
    }
    """
    processed = preprocessor.process(source)
    assert "SQUARE" not in processed
    assert "MAX" not in processed
    assert "((5) * (5))" in processed
    assert "((x) > (10) ? (x) : (10))" in processed

def test_preprocess_config_macros(preprocessor: Preprocessor):
    """Test preprocessing with configuration macros."""
    source = """
    int main() {
        #ifdef DEBUG
        return TEST;
        #else
        return 0;
        #endif
    }
    """
    processed = preprocessor.process(source)
    assert "DEBUG" not in processed
    assert "TEST" not in processed
    assert "42" in processed  # TEST macro value
    assert "#ifdef" not in processed
    assert "#else" not in processed
    assert "#endif" not in processed

def test_preprocess_error(preprocessor: Preprocessor):
    """Test handling preprocessing errors."""
    source = """
    #define SQUARE(x) x * x  // Missing parentheses
    int main() {
        return SQUARE(1 + 1);
    }
    """
    with pytest.raises(ParsingError):
        preprocessor.process(source) 