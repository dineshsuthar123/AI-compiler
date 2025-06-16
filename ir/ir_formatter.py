from typing import List, Dict
import re

class IRFormatter:
    """Formats LLVM IR code to be more human-friendly."""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_size = 2
        self.function_regex = re.compile(r'define\s+.*\s+@(\w+)\s*\(.*\)\s*{')
        self.label_regex = re.compile(r'(\w+):')
        self.instruction_regex = re.compile(r'\s+(\w+)\s+.*')
        
    def format(self, ir_code: str) -> str:
        """Format LLVM IR code to be more readable.
        
        Args:
            ir_code: Raw LLVM IR code
            
        Returns:
            Formatted LLVM IR code
        """
        lines = ir_code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                formatted_lines.append('')
                continue
                
            # Handle function definitions
            if self.function_regex.match(line):
                formatted_lines.append(line)
                self.indent_level += 1
                continue
                
            # Handle closing braces
            if line.strip() == '}':
                self.indent_level -= 1
                formatted_lines.append(' ' * (self.indent_level * self.indent_size) + '}')
                continue
                
            # Handle labels
            if self.label_regex.match(line):
                formatted_lines.append(' ' * ((self.indent_level - 1) * self.indent_size) + line)
                continue
                
            # Handle instructions
            if self.instruction_regex.match(line):
                formatted_lines.append(' ' * (self.indent_level * self.indent_size) + line.strip())
                continue
                
            # Handle other lines (metadata, attributes, etc.)
            formatted_lines.append(line)
            
        return '\n'.join(formatted_lines)
    
    def add_comments(self, ir_code: str) -> str:
        """Add explanatory comments to LLVM IR code.
        
        Args:
            ir_code: Formatted LLVM IR code
            
        Returns:
            LLVM IR code with explanatory comments
        """
        lines = ir_code.split('\n')
        commented_lines = []
        
        for line in lines:
            # Add comments for function definitions
            if self.function_regex.match(line):
                commented_lines.append('; Function definition')
                commented_lines.append(line)
                continue
                
            # Add comments for basic blocks
            if self.label_regex.match(line):
                commented_lines.append('; Basic block')
                commented_lines.append(line)
                continue
                
            # Add comments for common instructions
            if 'ret' in line:
                commented_lines.append('; Return statement')
                commented_lines.append(line)
                continue
                
            if 'alloca' in line:
                commented_lines.append('; Memory allocation')
                commented_lines.append(line)
                continue
                
            if 'store' in line:
                commented_lines.append('; Store value in memory')
                commented_lines.append(line)
                continue
                
            if 'load' in line:
                commented_lines.append('; Load value from memory')
                commented_lines.append(line)
                continue
                
            commented_lines.append(line)
            
        return '\n'.join(commented_lines)
    
    def format_with_comments(self, ir_code: str) -> str:
        """Format LLVM IR code and add explanatory comments.
        
        Args:
            ir_code: Raw LLVM IR code
            
        Returns:
            Formatted and commented LLVM IR code
        """
        formatted = self.format(ir_code)
        return self.add_comments(formatted) 