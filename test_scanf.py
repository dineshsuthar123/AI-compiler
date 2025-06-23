#!/usr/bin/env python3
"""
Test script to verify scanf implementation for user input.
"""

from simple_compiler import ModernCompiler

def test_scanf_basic():
    """Test basic scanf functionality."""
    print("=== Testing scanf for user input ===\n")
    
    c_code = '''
#include <stdio.h>

int main() {
    int number;
    printf("Enter a number: ");
    scanf("%d", &number);
    printf("You entered: %d\\n", number);
    return 0;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Compilation: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        if result['success']:
            print(f"Generated IR includes scanf: {'scanf' in result['ir_code']}")
            print(f"Program output: {result['output']}")
        else:
            print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scanf_multiple():
    """Test scanf with multiple inputs."""
    print("\n=== Testing scanf with multiple inputs ===\n")
    
    c_code = '''
#include <stdio.h>

int main() {
    int age;
    float height;
    
    printf("Enter your age: ");
    scanf("%d", &age);
    
    printf("Enter your height: ");
    scanf("%f", &height);
    
    printf("Age: %d, Height: %.2f\\n", age, height);
    return 0;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Compilation: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        if result['success']:
            print(f"Generated IR includes scanf: {'scanf' in result['ir_code']}")
            print(f"Program output: {result['output']}")
        else:
            print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run scanf tests."""
    print("Testing AI Compiler scanf Implementation")
    print("=" * 50)
    
    tests = [
        test_scanf_basic,
        test_scanf_multiple
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All scanf tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    main()
