import re
from pathlib import Path
from typing import Dict, List, Optional

class Preprocessor:
    """Handles C preprocessor directives."""
    
    def __init__(self, include_paths: Optional[List[str]] = None):
        """Initialize the preprocessor.
        
        Args:
            include_paths: List of paths to search for header files
        """
        self.include_paths = include_paths or []
        self.include_paths.append(str(Path(__file__).parent.parent / 'stdlib'))
        self.macros: Dict[str, str] = {}
          # Regular expressions for preprocessor directives
        self.include_regex = re.compile(r'#include\s*[<"]([^>"]+)[>"]')
        self.define_regex = re.compile(r'#define\s+(\w+)(?:\s+(.+))?')
        self.ifdef_regex = re.compile(r'#ifdef\s+(\w+)')
        self.ifndef_regex = re.compile(r'#ifndef\s+(\w+)')
        self.else_regex = re.compile(r'#else')
        self.endif_regex = re.compile(r'#endif')
        
    def find_header(self, header_name: str) -> Optional[str]:
        """Find a header file in the include paths.
        
        Args:
            header_name: Name of the header file
            
        Returns:
            Full path to the header file if found, None otherwise
        """
        for path in self.include_paths:
            header_path = Path(path) / header_name
            if header_path.exists():
                return str(header_path)
        return None
    
    def process_include(self, match: re.Match, processed_files: List[str]) -> str:
        """Process an #include directive.
        
        Args:
            match: Regex match object for the include directive
            processed_files: List of already processed files to avoid cycles
            
        Returns:
            The contents of the included file
        """
        header_name = match.group(1)
        header_path = self.find_header(header_name)
        
        if not header_path:
            raise FileNotFoundError(f"Header file not found: {header_name}")
            
        if header_path in processed_files:
            return "// Header already included\n"
            
        processed_files.append(header_path)
        
        with open(header_path, 'r') as f:
            content = f.read()
            
        return self.process(content, processed_files)
    
    def process_define(self, match: re.Match) -> str:
        """Process a #define directive.
        
        Args:
            match: Regex match object for the define directive
            
        Returns:
            Empty string (defines are handled during preprocessing)
        """
        name = match.group(1)
        value = match.group(2) or ''
        self.macros[name] = value
        return ''
    
    def expand_macros(self, line: str) -> str:
        """Expand macros in a line of code.
        
        Args:
            line: Line of code
            
        Returns:
            Line with macros expanded
        """
        for name, value in self.macros.items():
            line = re.sub(rf'\b{name}\b', value, line)
        return line
    
    def process(self, source: str, processed_files: Optional[List[str]] = None) -> str:
        """Process source code and handle preprocessor directives.
        
        Args:
            source: Source code to process
            processed_files: List of already processed files
              Returns:
            Processed source code
        """
        if processed_files is None:
            processed_files = []
            
        lines = source.split('\n')
        result = []
        conditional_stack = []  # Stack to handle nested conditionals
        
        for line in lines:
            # Handle #include
            include_match = self.include_regex.match(line)
            if include_match:
                if not conditional_stack or conditional_stack[-1]:
                    result.append(self.process_include(include_match, processed_files))
                continue
                
            # Handle #define
            define_match = self.define_regex.match(line)
            if define_match:
                if not conditional_stack or conditional_stack[-1]:
                    result.append(self.process_define(define_match))
                continue
                
            # Handle #ifdef
            ifdef_match = self.ifdef_regex.match(line)
            if ifdef_match:
                macro_name = ifdef_match.group(1)
                condition_met = macro_name in self.macros
                conditional_stack.append(condition_met)
                continue
                
            # Handle #ifndef
            ifndef_match = self.ifndef_regex.match(line)
            if ifndef_match:
                macro_name = ifndef_match.group(1)
                condition_met = macro_name not in self.macros
                conditional_stack.append(condition_met)
                continue
                
            # Handle #else
            if self.else_regex.match(line):
                if conditional_stack:
                    conditional_stack[-1] = not conditional_stack[-1]
                continue
                
            # Handle #endif
            if self.endif_regex.match(line):
                if conditional_stack:
                    conditional_stack.pop()
                continue
                
            # Skip lines if inside a false conditional block
            if conditional_stack and not conditional_stack[-1]:
                continue
                
            # Expand macros in the line
            processed_line = self.expand_macros(line)
            result.append(processed_line)
            
        return '\n'.join(result) 