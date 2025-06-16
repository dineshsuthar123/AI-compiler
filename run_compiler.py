from simple_compiler import ModernCompiler
import os
import sys

def main():
    # Check if source file is provided
    if len(sys.argv) < 2:
        print("Usage: python run_compiler.py <source_file>")
        sys.exit(1)
    
    # Get source file from command line argument
    source_file = sys.argv[1]
    
    # Initialize the compiler
    compiler = ModernCompiler()
    
    try:
        # Compile the source code
        print(f"Compiling {source_file}...")
        ir_code = compiler.compile(source_file, execute=False)
        
        # Print the generated LLVM IR
        print("\nGenerated LLVM IR:")
        print("=" * 40)
        print(ir_code)
        print("=" * 40)
        
        print(f"\nCompiler version: {compiler.version}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()