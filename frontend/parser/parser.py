from typing import Optional
from .c_parser import CParser

class Parser:
    """Wrapper class for the C parser."""
    
    def __init__(self):
        """Initialize the parser."""
        self._parser = CParser()
    
    def parse(self, source: str) -> Optional[object]:
        """Parse the given source code into an AST.
        
        Args:
            source: The source code to parse
            
        Returns:
            The root node of the AST if parsing succeeds, None otherwise
        """
        try:
            return self._parser.parse(source)
        except Exception as e:
            raise RuntimeError(f"Failed to parse source code: {str(e)}") 