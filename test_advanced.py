#!/usr/bin/env python3

from simple_compiler import ModernCompiler

def test_advanced_features():
    """Test advanced C features step by step."""
    compiler = ModernCompiler()
    
    tests = [ 
        {
            'name': 'Basic floating-point',
            'code': '''#include <stdio.h>
int main() {
    double x = 3.14;
    printf("Value: %.2f\\n", x);
    return 0;
}'''
        },
        {
            'name': 'Multiple variables',
            'code': '''#include <stdio.h>
int main() {
    double x = 3.14;
    double y = 2.71;
    double sum = x + y;
    printf("Sum: %.2f\\n", sum);
    return 0;
}'''
        },
        {
            'name': 'Basic arithmetic',
            'code': '''#include <stdio.h>
int main() {
    double a = 4.0;
    double b = 3.0;
    double result = a * a + b * b;
    printf("Result: %.1f\\n", result);
    return 0;
}'''
        },
        {
            'name': 'For loop with math',
            'code': '''#include <stdio.h>
int main() {
    double sum = 0.0;
    for (int i = 1; i <= 3; i++) {
        sum = sum + i * 1.5;
    }
    printf("Sum: %.1f\\n", sum);
    return 0;
}'''
        }
    ]
    
    print("Testing Advanced C Features")
    print("=" * 60)
    
    results = []
    for test in tests:
        print(f"\\nTest: {test['name']}")
        print("-" * 40)
        print("Code:")
        print(test['code'])
        print("\\nResult:")
        
        try:
            result = compiler.compile_and_execute(test['code'])
            if result['success']:
                print(f"SUCCESS: {result['output'].strip()}")
                results.append(True)
            else:
                print(f"FAILED: {result['error']}")
                results.append(False)
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append(False)
    
    print("\\n" + "=" * 60)
    print("Summary:")
    for i, (test, success) in enumerate(zip(tests, results)):
        status = "PASS" if success else "FAIL"
        print(f"  {i+1}. {test['name']}: {status}")
    
    passed = sum(results)
    total = len(results)
    print(f"\\nOverall: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    test_advanced_features()
