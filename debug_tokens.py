#!/usr/bin/env python3

from antlr4 import CommonTokenStream, InputStream
from frontend.grammar.CLexer import CLexer
from frontend.grammar.CParser import CParser

def debug_tokens():
    # Test the problematic code
    code = """
struct Point {
    float x;
    float y;
};

int main() {
    struct Point p;
    return 0;
}
"""
    print("Code to analyze:")
    print(code)
    print("\n" + "="*50)
    
    # Tokenize
    input_stream = InputStream(code)
    lexer = CLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    
    # Print all tokens
    print("TOKENS:")
    token_stream.fill()
    for i, token in enumerate(token_stream.tokens):
        if token.type != -1:  # Skip EOF
            token_name = lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else str(token.type)
            print(f"{i:2}: {token_name:15} '{token.text}'")
    
    print("\n" + "="*50)
    
    # Parse and print parse tree
    parser = CParser(token_stream)
    tree = parser.compilationUnit()
    
    print("PARSE TREE:")
    print(tree.toStringTree(recog=parser))

if __name__ == "__main__":
    debug_tokens()
