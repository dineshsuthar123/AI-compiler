#!/usr/bin/env python3
"""
Test script to verify preprocessor support for #include and #define directives.
"""

from simple_compiler import ModernCompiler

def test_include_stdio():
    """Test basic #include <stdio.h> support."""
    print("=== Testing #include <stdio.h> ===")
    
    c_code = '''
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_include_stdlib():
    """Test #include <stdlib.h> support."""
    print("\\n=== Testing #include <stdlib.h> ===")
    
    c_code = '''
#include <stdlib.h>

int main() {
    void* ptr = malloc(100);
    if (ptr != NULL) {
        free(ptr);
    }
    return 0;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_define_macros():
    """Test #define macro support."""
    print("\\n=== Testing #define macros ===")
    
    c_code = '''
#define MAX_SIZE 100
#define PI 3.14159

int main() {
    int size = MAX_SIZE;
    float pi_value = PI;
    return 0;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_multiple_includes():
    """Test multiple #include directives."""
    print("\\n=== Testing multiple #include ===")
    
    c_code = '''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char* str = malloc(20);
    strcpy(str, "Hello");
    printf("%s\\n", str);
    free(str);
    return 0;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_conditional_compilation():
    """Test #ifdef/#ifndef conditional compilation."""
    print("\\n=== Testing conditional compilation ===")
    
    c_code = '''
#define DEBUG

int main() {
#ifdef DEBUG
    int debug_mode = 1;
#else
    int debug_mode = 0;
#endif
    return debug_mode;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all preprocessor tests."""
    print("Testing AI Compiler Preprocessor Support")
    print("=" * 50)
    
    tests = [
        test_include_stdio,
        test_include_stdlib,
        test_define_macros,
        test_multiple_includes,
        test_conditional_compilation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All preprocessor tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    main()
