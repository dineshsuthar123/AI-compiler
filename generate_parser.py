import os
import subprocess
import sys
import shutil

def main():
    # Get the absolute path to the grammar file
    grammar_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'grammar')
    grammar_file = os.path.join(grammar_dir, 'C.g4')
    
    # Create grammar directory if it doesn't exist
    os.makedirs(grammar_dir, exist_ok=True)
    
    # Generate parser files
    cmd = f'antlr4 -Dlanguage=Python3 {grammar_file}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error generating parser files:")
        print(result.stderr)
        sys.exit(1)
    
    # Move generated files to grammar directory
    for file in ['CLexer.py', 'CParser.py', 'CVisitor.py', 'C.interp', 'C.tokens']:
        src = os.path.join(os.path.dirname(__file__), file)
        dst = os.path.join(grammar_dir, file)
        if os.path.exists(src):
            shutil.move(src, dst)
    
    print("Successfully generated parser files")

if __name__ == '__main__':
    main() 