#!/usr/bin/env python3

from simple_compiler import ModernCompiler

def test_floating_point():
    """Test floating-point number support."""
    compiler = ModernCompiler()
    
    # Simple floating point test
    test_code = '''#include <stdio.h>

int main() {
    double x = 3.14;
    printf("Value: %.2f\\n", x);
    return 0;
}'''
    
    print("Testing floating-point support...")
    print("Code to compile:")
    print(test_code)
    print("\n" + "="*50)
    
    try:
        result = compiler.compile_and_execute(test_code)
        print('SUCCESS!')
        print('Result:', result)
        return True
    except Exception as e:
        print('ERROR:', str(e))
        return False

def test_simple_hello():
    """Test simple hello world."""
    compiler = ModernCompiler()
    
    # Simple hello world test
    test_code = '''#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}'''
    
    print("\nTesting simple hello world...")
    print("Code to compile:")
    print(test_code)
    print("\n" + "="*50)
    
    try:
        result = compiler.compile_and_execute(test_code)
        print('SUCCESS!')
        print('Result:', result)
        return True
    except Exception as e:
        print('ERROR:', str(e))
        return False

if __name__ == "__main__":
    print("Testing AI Compiler Improvements")
    print("="*60)
    
    # Test basic functionality first
    success1 = test_simple_hello()
    
    # Test floating point
    success2 = test_floating_point()
    
    print("\n" + "="*60)
    print(f"Results: Hello World: {'✓' if success1 else '✗'}, Float: {'✓' if success2 else '✗'}")
