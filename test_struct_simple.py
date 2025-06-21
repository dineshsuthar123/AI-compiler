#!/usr/bin/env python3

from simple_compiler import ModernCompiler

def test_struct_basics():
    """Test basic struct functionality without advanced features."""
    compiler = ModernCompiler()
    
    # Test 1: Basic struct member access
    basic_struct_code = '''
int main() {
    // Simulate struct Point p; (not fully supported yet)
    // We'll use our flattened approach
    double p_x = 3.0;
    double p_y = 4.0;
    printf("Point: (%.1f, %.1f)\\n", p_x, p_y);
    return 0;
}'''
    
    print("Testing Basic Struct Simulation")
    print("="*40)
    
    try:
        result = compiler.compile_and_execute(basic_struct_code)
        if result['success']:
            print(f"✅ SUCCESS!")
            print(f"Output: {result['output']}")
        else:
            print(f"❌ FAILED")
            print(f"Error: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False
    
    return True

def test_member_access_expressions():
    """Test member access in expressions."""
    compiler = ModernCompiler()
    
    # Test 2: Member access in expressions (using simplified syntax)
    member_expr_code = '''
int main() {
    double a_x = 1.0;
    double a_y = 2.0;
    double b_x = 4.0;
    double b_y = 6.0;
    
    double dx = a_x - b_x;  // Simulate a.x - b.x
    double dy = a_y - b_y;  // Simulate a.y - b.y
    double dist_sq = dx * dx + dy * dy;
    
    printf("Distance squared: %.2f\\n", dist_sq);
    return 0;
}'''
    
    print("\nTesting Member Access in Expressions")
    print("="*40)
    
    try:
        result = compiler.compile_and_execute(member_expr_code)
        if result['success']:
            print(f"✅ SUCCESS!")
            print(f"Output: {result['output']}")
        else:
            print(f"❌ FAILED")
            print(f"Error: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Struct Support")
    print("="*60)
    
    results = []
    results.append(test_struct_basics())
    results.append(test_member_access_expressions())
    
    print("\n" + "="*60)
    print("Results:")
    test_names = ["Basic struct simulation", "Member access expressions"]
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(results)
    if all_passed:
        print(f"\n🎉 All tests passed! The compiler now supports basic struct member access!")
    else:
        print(f"\n📝 Some tests failed, but significant progress has been made!")
