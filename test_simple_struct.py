#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.parser.c_parser import CParser
from ir.ir_generator import IRGenerator

def test_simple_struct():
    """Test a very simple struct case."""
    
    code = '''
    struct Point {
        int x;
        int y;
    };
    
    int main() {
        struct Point p;
        p.x = 42;
        return 0;
    }
    '''
    
    print("🧪 Testing Simple Struct")
    print("=" * 50)
    print("Code:")
    print(code)
    print("-" * 40)
    
    try:
        # Parse
        parser = CParser()
        ast = parser.parse(code)
        print("✓ Parsed successfully")
        
        # Generate IR
        generator = IRGenerator()
        generator.visit(ast)
        ir_code = generator.get_ir()
        print("✓ Generated IR successfully")
        
        print("\nGenerated IR:")
        print(ir_code)
        
        # Check for proper struct support
        if "{i32, i32}" in ir_code and "getelementptr" in ir_code:
            print("\n✅ Real struct support working!")
        else:
            print("\n❌ Falling back to flattened variables")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_struct()
