#!/usr/bin/env python3
"""
Test script for real struct support in the AI C compiler.
Tests actual struct types and struct variables.
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from frontend.parser.c_parser import CParser
from ir.ir_generator import IRGenerator

def test_real_struct():
    """Test real struct variable declaration and usage."""
    print("🧪 Testing Real Struct Support")
    print("="*50)
    
    # Test code with struct declaration and struct variable
    code = """
    struct Point {
        int x;
        int y;
        float z;
    };
    
    int main() {
        struct Point p;
        p.x = 42;
        p.y = 24; 
        p.z = 3.14;
        return 0;
    }
    """
    
    print("Code to compile:")
    print(code)
    print("-" * 40)
    
    try:
        # Parse the code
        parser = CParser()
        ast = parser.parse(code)
        print("✓ Parsed successfully")
        
        # Print AST structure
        print(f"AST: {ast.__class__.__name__}")
        for i, decl in enumerate(ast.declarations):
            print(f"  Declaration {i}: {decl.__class__.__name__}")
            if hasattr(decl, 'name'):
                print(f"    Name: {decl.name}")
            
            if decl.__class__.__name__ == 'StructDecl':
                print(f"    Fields:")
                for field in decl.fields:
                    print(f"      - {field.name}: {field.type.name}")
        
        # Generate IR
        generator = IRGenerator()
        generator.visit(ast)
        
        print("✓ Generated IR successfully")
        
        # Check if struct types were created
        if hasattr(generator, 'struct_types'):
            print(f"✓ Struct types created: {list(generator.struct_types.keys())}")
            for struct_name, struct_info in generator.struct_types.items():
                print(f"  {struct_name}:")
                print(f"    Fields: {struct_info['fields']}")
                print(f"    Types: {struct_info['field_types']}")
        else:
            print("⚠️ No struct types found")
        
        # Check symbol table
        print(f"Symbol table: {list(generator.symbol_table.keys())}")
        
        # Display IR
        ir_code = generator.get_ir()
        print(f"Generated IR ({len(ir_code)} chars):")
        print(ir_code)
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_real_struct()
    if success:
        print("\n🎉 Real struct test completed!")
    else:
        print("\n❌ Real struct test failed!")
