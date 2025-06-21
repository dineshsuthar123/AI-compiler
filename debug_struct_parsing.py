#!/usr/bin/env python3
"""
Debug script to understand how struct variable declarations are parsed.
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from frontend.parser.c_parser import CParser

def debug_struct_parsing():
    """Debug struct variable declaration parsing."""
    print("🔍 Debugging Struct Variable Parsing")
    print("="*50)
    
    # Simple struct variable declaration
    code = """
    struct Point {
        int x;
        int y;
    };
    
    int main() {
        struct Point p;
        return 0;
    }
    """
    
    print("Code to debug:")
    print(code)
    print("-" * 40)
    
    try:
        # Parse the code
        parser = CParser()
        ast = parser.parse(code)
        print("✓ Parsed successfully")
        
        # Analyze the AST structure
        print(f"AST: {ast.__class__.__name__}")
        for i, decl in enumerate(ast.declarations):
            print(f"  Declaration {i}: {decl.__class__.__name__}")
            if hasattr(decl, 'name'):
                print(f"    Name: {decl.name}")
            
            if hasattr(decl, 'body') and decl.body:
                print(f"    Body: {decl.body.__class__.__name__}")
                if hasattr(decl.body, 'statements'):
                    print(f"    Statements ({len(decl.body.statements)}):")
                    for j, stmt in enumerate(decl.body.statements):
                        print(f"      Statement {j}: {stmt.__class__.__name__}")
                        if hasattr(stmt, 'name'):
                            print(f"        Name: {stmt.name}")
                        if hasattr(stmt, 'type'):
                            print(f"        Type: {stmt.type.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = debug_struct_parsing()
    if success:
        print("\n🎉 Debug completed!")
    else:
        print("\n❌ Debug failed!")
