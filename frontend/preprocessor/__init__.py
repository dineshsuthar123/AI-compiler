from typing import Dict, List, Optional, Pattern
import re
from pathlib import Path
import logging
from .. import FrontendPlugin

class PreprocessorPlugin(FrontendPlugin):
    """Modern preprocessor plugin with advanced features."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.macros: Dict[str, str] = {}
        self.include_paths: List[str] = []
        self.conditional_stack: List[bool] = []
        self.config: Dict = {}
        
        # Regular expressions for preprocessor directives
        self.directives: Dict[str, Pattern] = {
            'include': re.compile(r'#include\s*[<"]([^>"]+)[>"]'),
            'define': re.compile(r'#define\s+(\w+)(?:\s+(.+))?'),
            'undef': re.compile(r'#undef\s+(\w+)'),
            'ifdef': re.compile(r'#ifdef\s+(\w+)'),
            'ifndef': re.compile(r'#ifndef\s+(\w+)'),
            'if': re.compile(r'#if\s+(.+)'),
            'else': re.compile(r'#else'),
            'elif': re.compile(r'#elif\s+(.+)'),
            'endif': re.compile(r'#endif'),
            'pragma': re.compile(r'#pragma\s+(.+)'),
            'error': re.compile(r'#error\s+(.+)'),
            'warning': re.compile(r'#warning\s+(.+)'),
        }
        
        # Initialize built-in macros
        self._init_builtin_macros()
    
    def _init_builtin_macros(self) -> None:
        """Initialize built-in macros."""
        self.macros.update({
            '__FILE__': '"__FILE__"',
            '__LINE__': '__LINE__',
            '__DATE__': '"__DATE__"',
            '__TIME__': '"__TIME__"',
            '__STDC__': '1',
            '__STDC_VERSION__': '201112L',
            '__STDC_HOSTED__': '1',
            '__cplusplus': '0',
        })
    
    def initialize(self, config: Dict) -> None:
        """Initialize the preprocessor with configuration."""
        self.config = config
        self.include_paths = config.get('include_paths', [])
        self.macros.update(config.get('macros', {}))
    
    def get_name(self) -> str:
        return "preprocessor"
    
    def process(self, source: str) -> str:
        """Process the source code through the preprocessor."""
        lines = source.split('\n')
        output = []
        self.conditional_stack = [True]  # Start with true to process normally
        
        for line in lines:
            processed_line = self._process_line(line)
            if processed_line is not None:
                output.append(processed_line)
        
        return '\n'.join(output)
    
    def _process_line(self, line: str) -> Optional[str]:
        """Process a single line of source code."""
        # Check if we should process this line based on conditional stack
        if not self.conditional_stack[-1]:
            return None
        
        # Check for preprocessor directives
        for directive, pattern in self.directives.items():
            match = pattern.match(line.strip())
            if match:
                return self._handle_directive(directive, match)
        
        # Process macros in the line
        return self._expand_macros(line)
    
    def _handle_directive(self, directive: str, match: re.Match) -> Optional[str]:
        """Handle a preprocessor directive."""
        if directive == 'include':
            return self._handle_include(match)
        elif directive == 'define':
            self._handle_define(match)
            return None
        elif directive == 'undef':
            self._handle_undef(match)
            return None
        elif directive == 'ifdef':
            self._handle_ifdef(match)
            return None
        elif directive == 'ifndef':
            self._handle_ifndef(match)
            return None
        elif directive == 'if':
            self._handle_if(match)
            return None
        elif directive == 'else':
            self._handle_else()
            return None
        elif directive == 'elif':
            self._handle_elif(match)
            return None
        elif directive == 'endif':
            self._handle_endif()
            return None
        elif directive == 'pragma':
            self._handle_pragma(match)
            return None
        elif directive == 'error':
            self._handle_error(match)
            return None
        elif directive == 'warning':
            self._handle_warning(match)
            return None
        
        return None
    
    def _handle_include(self, match: re.Match) -> str:
        """Handle #include directive."""
        header = match.group(1)
        header_path = self._find_header(header)
        
        if not header_path:
            raise FileNotFoundError(f"Header file not found: {header}")
        
        with open(header_path, 'r') as f:
            content = f.read()
        
        return self.process(content)
    
    def _find_header(self, header: str) -> Optional[str]:
        """Find a header file in the include paths."""
        for path in self.include_paths:
            header_path = Path(path) / header
            if header_path.exists():
                return str(header_path)
        return None
    
    def _handle_define(self, match: re.Match) -> None:
        """Handle #define directive."""
        name = match.group(1)
        value = match.group(2) or ''
        self.macros[name] = value
    
    def _handle_undef(self, match: re.Match) -> None:
        """Handle #undef directive."""
        name = match.group(1)
        if name in self.macros:
            del self.macros[name]
    
    def _handle_ifdef(self, match: re.Match) -> None:
        """Handle #ifdef directive."""
        name = match.group(1)
        self.conditional_stack.append(name in self.macros)
    
    def _handle_ifndef(self, match: re.Match) -> None:
        """Handle #ifndef directive."""
        name = match.group(1)
        self.conditional_stack.append(name not in self.macros)
    
    def _handle_if(self, match: re.Match) -> None:
        """Handle #if directive."""
        condition = match.group(1)
        # TODO: Implement expression evaluation
        self.conditional_stack.append(True)
    
    def _handle_else(self) -> None:
        """Handle #else directive."""
        if len(self.conditional_stack) > 1:
            self.conditional_stack[-1] = not self.conditional_stack[-1]
    
    def _handle_elif(self, match: re.Match) -> None:
        """Handle #elif directive."""
        if len(self.conditional_stack) > 1:
            condition = match.group(1)
            # TODO: Implement expression evaluation
            self.conditional_stack[-1] = True
    
    def _handle_endif(self) -> None:
        """Handle #endif directive."""
        if len(self.conditional_stack) > 1:
            self.conditional_stack.pop()
    
    def _handle_pragma(self, match: re.Match) -> None:
        """Handle #pragma directive."""
        pragma = match.group(1)
        self.logger.info(f"Pragma directive: {pragma}")
    
    def _handle_error(self, match: re.Match) -> None:
        """Handle #error directive."""
        message = match.group(1)
        raise Exception(f"Preprocessor error: {message}")
    
    def _handle_warning(self, match: re.Match) -> None:
        """Handle #warning directive."""
        message = match.group(1)
        self.logger.warning(f"Preprocessor warning: {message}")
    
    def _expand_macros(self, line: str) -> str:
        """Expand macros in a line of code."""
        result = line
        for name, value in self.macros.items():
            result = re.sub(rf'\b{name}\b', value, result)
        return result

# Create the plugin instance
Plugin = PreprocessorPlugin() 