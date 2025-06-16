import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
from typing import List

from compiler.cli import main, handle_compile, handle_web

@pytest.fixture
def args():
    """Create test command line arguments."""
    class Args:
        def __init__(self):
            self.command = None
            self.source = None
            self.output = None
            self.config = None
            self.optimization_level = None
            self.host = None
            self.port = None
    return Args()

def test_main_no_command(capsys):
    """Test main function with no command."""
    sys.argv = ["compiler"]
    assert main() == 1
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower()

def test_main_invalid_command(capsys):
    """Test main function with invalid command."""
    sys.argv = ["compiler", "invalid"]
    assert main() == 1
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower()

@patch("compiler.cli.handle_compile")
def test_main_compile(mock_handle_compile, args):
    """Test main function with compile command."""
    mock_handle_compile.return_value = 0
    args.command = "compile"
    args.source = "test.c"
    assert main([args.command, args.source]) == 0
    mock_handle_compile.assert_called_once()

@patch("compiler.cli.handle_web")
def test_main_web(mock_handle_web, args):
    """Test main function with web command."""
    mock_handle_web.return_value = 0
    args.command = "web"
    assert main([args.command]) == 0
    mock_handle_web.assert_called_once()

@patch("compiler.core.Compiler")
def test_handle_compile_success(mock_compiler, args, tmp_path):
    """Test handle_compile with successful compilation."""
    source = tmp_path / "test.c"
    source.write_text("int main() { return 0; }")
    args.source = str(source)
    
    mock_instance = MagicMock()
    mock_instance.compile.return_value = {"success": True}
    mock_compiler.return_value = mock_instance
    
    assert handle_compile(args) == 0
    mock_instance.compile.assert_called_once()

@patch("compiler.core.Compiler")
def test_handle_compile_error(mock_compiler, args, tmp_path):
    """Test handle_compile with compilation error."""
    source = tmp_path / "test.c"
    source.write_text("invalid code")
    args.source = str(source)
    
    mock_instance = MagicMock()
    mock_instance.compile.side_effect = Exception("Compilation failed")
    mock_compiler.return_value = mock_instance
    
    assert handle_compile(args) == 1

def test_handle_compile_nonexistent_file(args):
    """Test handle_compile with nonexistent file."""
    args.source = "nonexistent.c"
    assert handle_compile(args) == 1

@patch("compiler.web.create_app")
def test_handle_web(mock_create_app, args):
    """Test handle_web function."""
    mock_app = MagicMock()
    mock_create_app.return_value = mock_app
    
    args.host = "127.0.0.1"
    args.port = 5000
    
    assert handle_web(args) == 0
    mock_app.run.assert_called_once_with(host=args.host, port=args.port)

def test_handle_compile_with_config(args, tmp_path):
    """Test handle_compile with custom configuration."""
    source = tmp_path / "test.c"
    source.write_text("int main() { return 0; }")
    args.source = str(source)
    
    config = tmp_path / "config.yaml"
    config.write_text("compilation:\n  optimization_level: 3")
    args.config = str(config)
    
    with patch("compiler.core.Compiler") as mock_compiler:
        mock_instance = MagicMock()
        mock_instance.compile.return_value = {"success": True}
        mock_compiler.return_value = mock_instance
        
        assert handle_compile(args) == 0
        mock_compiler.assert_called_once()

def test_handle_compile_with_optimization(args, tmp_path):
    """Test handle_compile with optimization level."""
    source = tmp_path / "test.c"
    source.write_text("int main() { return 0; }")
    args.source = str(source)
    args.optimization_level = 3
    
    with patch("compiler.core.Compiler") as mock_compiler:
        mock_instance = MagicMock()
        mock_instance.compile.return_value = {"success": True}
        mock_compiler.return_value = mock_instance
        
        assert handle_compile(args) == 0
        mock_instance.config.set.assert_called_with(
            "compilation.optimization_level", 3
        ) 