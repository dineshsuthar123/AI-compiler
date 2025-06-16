import argparse
import sys
from pathlib import Path
from typing import Optional

from compiler.core import Compiler
from compiler.config import ConfigLoader
from compiler.exceptions import CompilerError

def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="AI-powered compiler with modern features"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Compile command
    compile_parser = subparsers.add_parser("compile", help="Compile source code")
    compile_parser.add_argument("source", type=str, help="Source file to compile")
    compile_parser.add_argument(
        "-o", "--output", type=str, help="Output file path"
    )
    compile_parser.add_argument(
        "--config", type=str, help="Path to configuration file"
    )
    compile_parser.add_argument(
        "--optimization-level", type=int, choices=range(5),
        help="Optimization level (0-4)"
    )
    
    # Web server command
    web_parser = subparsers.add_parser("web", help="Start web server")
    web_parser.add_argument(
        "--host", type=str, default="0.0.0.0",
        help="Host to bind the server to"
    )
    web_parser.add_argument(
        "--port", type=int, default=5000,
        help="Port to bind the server to"
    )
    
    args = parser.parse_args(argv)
    
    try:
        if args.command == "compile":
            return handle_compile(args)
        elif args.command == "web":
            return handle_web(args)
        else:
            parser.print_help()
            return 1
    except CompilerError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

def handle_compile(args: argparse.Namespace) -> int:
    """Handle the compile command."""
    config = ConfigLoader(args.config)
    
    if args.optimization_level is not None:
        config.set("compilation.optimization_level", args.optimization_level)
    
    compiler = Compiler(config)
    
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source file {source_path} does not exist", file=sys.stderr)
        return 1
    
    output_path = Path(args.output) if args.output else source_path.with_suffix(".ll")
    
    try:
        result = compiler.compile(source_path, output_path)
        print(f"Successfully compiled {source_path} to {output_path}")
        return 0
    except CompilerError as e:
        print(f"Compilation failed: {e}", file=sys.stderr)
        return 1

def handle_web(args: argparse.Namespace) -> int:
    """Handle the web server command."""
    from compiler.web import create_app
    
    app = create_app()
    app.run(host=args.host, port=args.port)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 