# test_c_parser.py
from frontend.parser.c_parser import CParser
from ir.ir_generator import IRGenerator

def preprocess_c_code(source_code: str) -> str:
    # Remove preprocessor lines (lines starting with #)
    lines = source_code.splitlines()
    lines = [line for line in lines if not line.strip().startswith('#')]
    code = '\n'.join(lines)
    # Transform for-loop declarations: for (int i = 0; ...; ...) -> int i; for (i = 0; ...; ...)
    import re
    def for_decl_replacer(match):
        decl = match.group(1)
        rest = match.group(2)
        # Extract variable name and init value
        var_match = re.match(r'\s*int\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^;]+)', decl)
        if var_match:
            var_name = var_match.group(1)
            var_init = var_match.group(2)
            return f'int {var_name};\nfor ({var_name} = {var_init};{rest})'
        return match.group(0)
    # Updated regex with capturing groups for declaration and rest
    code = re.sub(r'for\s*\(\s*int\s+[^;]+;([^\)]*)\)', lambda m: for_decl_replacer(re.match(r'for\s*\(\s*int\s+([^;]+);([^\)]*)\)', m.group(0))), code)
    return code

def main():
    # Read C source code
    with open('examples/test_complex.c', 'r') as f:
        source_code = f.read()
    
    # Preprocess: remove preprocessor lines and transform for-loops
    source_code = preprocess_c_code(source_code)
    
    # Parse C code to AST
    parser = CParser()
    ast = parser.parse(source_code)
    
    # Generate IR from AST
    ir_generator = IRGenerator()
    ir_generator.visit(ast)
    
    # Print the generated IR
    print(str(ir_generator.module))

if __name__ == '__main__':
    main()