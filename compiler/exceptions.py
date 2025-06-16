class CompilerError(Exception):
    """Base exception class for compiler errors."""
    pass

class ConfigurationError(CompilerError):
    """Raised when there is an error in the configuration."""
    pass

class ParsingError(CompilerError):
    """Raised when there is an error parsing the source code."""
    pass

class IRGenerationError(CompilerError):
    """Raised when there is an error generating IR code."""
    pass

class OptimizationError(CompilerError):
    """Raised when there is an error during optimization."""
    pass

class PluginError(CompilerError):
    """Raised when there is an error in a plugin."""
    pass

class AIAnalysisError(CompilerError):
    """Raised when there is an error in AI analysis."""
    pass

class ValidationError(CompilerError):
    """Raised when there is a validation error."""
    pass

class FileSystemError(CompilerError):
    """Raised when there is an error accessing the file system."""
    pass 