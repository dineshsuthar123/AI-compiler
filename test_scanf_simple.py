#!/usr/bin/env python3
"""
Simple test to check address-of operator and scanf call parsing.
"""

from simple_compiler import ModernCompiler

def test_address_of_operator():
    """Test if the address-of operator is parsed correctly."""
    print("=== Testing address-of operator (&) ===\n")
    
    c_code = '''
int main() {
    int x = 42;
    int* ptr = &x;
    return 0;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Compilation: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        if not result['success']:
            print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_simple_scanf():
    """Test very simple scanf without preprocessing."""
    print("\n=== Testing simple scanf without includes ===\n")
    
    c_code = '''
int scanf(char* format, ...);

int main() {
    int num;
    scanf("%d", &num);
    return 0;
}
'''
    
    try:
        compiler = ModernCompiler()
        result = compiler.compile_and_execute(c_code)
        print(f"Compilation: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        if result['success']:
            print("✅ Simple scanf compiled successfully")
            print(f"IR contains scanf call: {'scanf' in result['ir_code']}")
        else:
            print(f"Errors: {result['errors']}")
        return result['success']
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run simple scanf tests."""
    print("Testing scanf Issues")
    print("=" * 30)
    
    tests = [
        test_address_of_operator,
        test_simple_scanf
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")

if __name__ == "__main__":
    main()
