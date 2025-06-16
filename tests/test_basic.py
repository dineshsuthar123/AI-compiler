import pytest
from pathlib import Path
import os
from ..compiler import Compiler

def test_compiler_initialization():
    """Test that compiler initializes correctly."""
    compiler = Compiler()
    assert compiler.version == "0.1.0"
    assert compiler.parser is not None
    assert compiler.ir_generator is not None
    assert compiler.feature_extractor is not None
    assert compiler.ai_optimizer is not None

def test_simple_compilation():
    """Test compilation of a simple C program."""
    source_code = """
    int add(int a, int b) {
        return a + b;
    }
    """
    
    compiler = Compiler()
    output_file = compiler.compile(source_code)
    
    assert Path(output_file).exists()
    assert Path(output_file).stat().st_size > 0 