#!/usr/bin/env python3
"""
Test comprehensive struct support in the C compiler.
This test validates:
1. Struct declaration parsing
2. Struct variable declarations
3. Member access expressions
4. IR generation for struct types
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_struct_declaration():
    """Test parsing of struct declarations."""
    print("=== Testing Struct Declaration ===")
    
    from frontend.parser.c_parser import CParser
    from frontend.ast.nodes import StructDecl, VariableDecl, Type
    
    # Test struct declaration
    code = """
    struct Point {
        int x;
        int y;
        float z;
    };
    """
    
    try:
        parser = CParser()
        ast = parser.parse(code)
        print(f"✓ Parsed struct declaration successfully")
        print(f"  AST: {type(ast).__name__}")
        
        # Check if we have struct declarations
        for decl in ast.declarations:
            if isinstance(decl, StructDecl):
                print(f"  ✓ Found struct: {decl.name}")
                for field in decl.fields:
                    print(f"    - {field.name}: {field.type.name}")
                return True
        
        print("  ⚠ No struct declarations found in AST")
        return False
        
    except Exception as e:
        print(f"  ✗ Error parsing struct declaration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_struct_variable():
    """Test parsing of struct variable declarations."""
    print("\n=== Testing Struct Variable Declaration ===")
    
    from frontend.parser.c_parser import CParser
    from frontend.ast.nodes import VariableDecl
    
    # Test struct variable declaration
    code = """
    struct Point {
        int x;
        int y;
    };
    
    int main() {
        struct Point p;
        p.x = 10;
        p.y = 20;
        return 0;
    }
    """
    
    try:
        parser = CParser()
        ast = parser.parse(code)
        print(f"✓ Parsed struct variable declaration successfully")
        
        # Look for struct variable declarations
        found_struct_var = False
        for decl in ast.declarations:
            print(f"  Declaration: {type(decl).__name__}")
            if hasattr(decl, 'body') and decl.body:
                for stmt in decl.body.statements:
                    print(f"    Statement: {type(stmt).__name__}")
                    if isinstance(stmt, VariableDecl) and stmt.type.name.startswith('struct'):
                        print(f"    ✓ Found struct variable: {stmt.name} of type {stmt.type.name}")
                        found_struct_var = True
        
        return found_struct_var
        
    except Exception as e:
        print(f"  ✗ Error parsing struct variable: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_struct_ir_generation():
    """Test IR generation for structs."""
    print("\n=== Testing Struct IR Generation ===")
    
    from frontend.parser.c_parser import CParser
    from ir.ir_generator import IRGenerator
    from frontend.ast.nodes import StructDecl
    
    # Test struct IR generation
    code = """
    struct Point {
        int x;
        int y;
        double z;
    };
    
    int main() {
        struct Point p;
        p.x = 42;
        p.y = 24;
        p.z = 3.14;
        return 0;
    }
    """
    
    try:
        parser = CParser()
        ast = parser.parse(code)
        print(f"✓ Parsed code successfully")
        
        # Generate IR
        generator = IRGenerator()
        generator.visit(ast)
        ir_code = generator.get_ir()
        
        print(f"✓ Generated IR successfully")
        print(f"  IR length: {len(ir_code)} characters")
        
        # Check for struct-related elements in IR
        if 'struct' in ir_code.lower():
            print(f"  ✓ IR contains struct-related code")
        else:
            print(f"  ⚠ IR doesn't contain obvious struct references")
            
        # Show a snippet of the IR
        print(f"\n  IR snippet (first 500 chars):")
        print(f"  {ir_code[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error generating struct IR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_member_access():
    """Test member access expressions."""
    print("\n=== Testing Member Access ===")
    
    from frontend.parser.c_parser import CParser
    from ir.ir_generator import IRGenerator
    
    # Test member access
    code = """
    int main() {
        struct Point p;
        p.x = 100;
        p.y = 200;
        int sum = p.x + p.y;
        return sum;
    }
    """
    
    try:
        parser = CParser()
        ast = parser.parse(code)
        print(f"✓ Parsed member access successfully")
        
        # Generate IR
        generator = IRGenerator()
        generator.visit(ast)
        ir_code = generator.get_ir()
        
        print(f"✓ Generated IR for member access")
        
        # Check for member access variables in the symbol table
        if hasattr(generator, 'symbol_table'):
            member_vars = [name for name in generator.symbol_table.keys() if '_' in name]
            if member_vars:
                print(f"  ✓ Found member variables: {member_vars}")
            else:
                print(f"  ⚠ No member variables found in symbol table")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error with member access: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all struct tests."""
    print("🏗️  Testing Comprehensive Struct Support")
    print("=" * 50)
    
    tests = [
        test_struct_declaration,
        test_struct_variable,
        test_struct_ir_generation,
        test_member_access,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All struct tests passed!")
        return True
    else:
        print("⚠️  Some struct tests failed. More work needed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
