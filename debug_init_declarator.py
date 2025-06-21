#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from antlr4 import *
from frontend.grammar.CParser import CParser as AntlrCParser
from frontend.grammar.CLexer import CLexer
from frontend.grammar.CListener import CListener

class InitDeclaratorDebugListener(CListener):
    """Debug listener to examine initDeclaratorList structure."""
    
    def __init__(self):
        self.indent_level = 0
    
    def print_debug(self, msg):
        print("  " * self.indent_level + msg)
    
    def enterDeclaration(self, ctx):
        """Enter a parse tree produced by CParser.declaration."""
        self.print_debug(f"=== DECLARATION: {ctx.getText()} ===")
        self.indent_level += 1
        
        # Check if there's an initDeclaratorList
        if ctx.initDeclaratorList():
            self.print_debug(f"HAS initDeclaratorList: {ctx.initDeclaratorList().getText()}")
            self.print_debug(f"initDeclaratorList children count: {len(ctx.initDeclaratorList().children)}")
            
            # Examine each child of initDeclaratorList
            for i, child in enumerate(ctx.initDeclaratorList().children):
                self.print_debug(f"  Child {i}: {type(child).__name__} = '{child.getText()}'")
                
                # If it's an initDeclarator, examine its structure
                if hasattr(child, 'getRuleIndex'):
                    try:
                        if hasattr(child, 'declarator'):
                            self.print_debug(f"    Has declarator: {child.declarator().getText() if child.declarator() else 'None'}")
                            if child.declarator() and child.declarator().directDeclarator():
                                direct_decl = child.declarator().directDeclarator()
                                self.print_debug(f"    DirectDeclarator: {direct_decl.getText()}")
                                if direct_decl.Identifier():
                                    self.print_debug(f"    Identifier: {direct_decl.Identifier().getText()}")
                        if hasattr(child, 'initializer'):
                            self.print_debug(f"    Has initializer: {child.initializer().getText() if child.initializer() else 'None'}")
                    except Exception as e:
                        self.print_debug(f"    Error examining child: {e}")
            
            # Also examine initDeclarator() method calls
            try:
                init_declarators = ctx.initDeclaratorList().initDeclarator()
                self.print_debug(f"initDeclarator() method returns {len(init_declarators)} items:")
                for i, init_decl in enumerate(init_declarators):
                    self.print_debug(f"  InitDeclarator {i}: {init_decl.getText()}")
                    if init_decl.declarator():
                        self.print_debug(f"    Declarator: {init_decl.declarator().getText()}")
                        if init_decl.declarator().directDeclarator():
                            direct_decl = init_decl.declarator().directDeclarator()
                            if direct_decl.Identifier():
                                self.print_debug(f"    Variable name: {direct_decl.Identifier().getText()}")
                    if init_decl.initializer():
                        self.print_debug(f"    Initializer: {init_decl.initializer().getText()}")
            except Exception as e:
                self.print_debug(f"Error calling initDeclarator(): {e}")
        else:
            self.print_debug("NO initDeclaratorList")
    
    def exitDeclaration(self, ctx):
        """Exit a parse tree produced by CParser.declaration."""
        self.indent_level -= 1
    
    def enterCompoundStatement(self, ctx):
        """Enter a parse tree produced by CParser.compoundStatement."""
        self.print_debug(f"=== COMPOUND STATEMENT ===")
        self.indent_level += 1
    
    def exitCompoundStatement(self, ctx):
        """Exit a parse tree produced by CParser.compoundStatement."""
        self.indent_level -= 1

def debug_init_declarator():
    """Debug the initDeclaratorList structure."""
    
    # Test code with struct variable declaration
    test_code = """
int main() {
    struct Point p;
    int x = 5;
    return 0;
}
"""
    
    print("=== DEBUGGING INIT DECLARATOR LIST ===")
    print(f"Test code:\n{test_code}")
    print("\n=== PARSING RESULTS ===")
    
    # Create lexer and parser
    input_stream = InputStream(test_code)
    lexer = CLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = AntlrCParser(token_stream)
    
    # Parse the input
    tree = parser.compilationUnit()
    
    # Walk the tree with our debug listener
    debug_listener = InitDeclaratorDebugListener()
    walker = ParseTreeWalker()
    walker.walk(debug_listener, tree)
    
    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    debug_init_declarator()
