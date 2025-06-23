#!/usr/bin/env python3
"""
Test scanf with fixed address-of operator.
"""

from simple_compiler import ModernCompiler

def test_scanf_with_address_of():
    """Test scanf with proper address-of operator support."""
    print("=== Testing scanf with fixed address-of operator ===\n")
    
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
            print(f"Generated IR:\n{result['ir_code']}")
            print(f"Program output: {result['output']}")
            
            # Check if the IR contains the correct scanf call with pointer
            ir_code = result['ir_code']
            has_scanf = 'scanf' in ir_code
            has_pointer_arg = 'alloca' in ir_code and 'scanf' in ir_code
            
            print(f"✅ Contains scanf: {has_scanf}")
            print(f"✅ Uses pointer argument: {has_pointer_arg}")
            
        else:
            print(f"❌ Errors: {result['errors']}")
            
        return result['success']
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_scanf_with_address_of()
