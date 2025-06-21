import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    # Try to import the module
    from ir.ir_generator import IRGenerator
    print('Module imports successfully')
    
    # Try to create an instance
    generator = IRGenerator()
    print('IRGenerator instance created successfully')
    
    # Test a simple method
    print(f'Module: {generator.module}')
    print('All tests passed!')
    
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
