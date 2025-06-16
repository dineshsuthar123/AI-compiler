"""Plugin system for the AI compiler."""

from compiler.plugins.base import (
    BasePlugin,
    PreprocessorPlugin,
    ASTAnalyzerPlugin,
    IROptimizerPlugin
)

__all__ = [
    "BasePlugin",
    "PreprocessorPlugin",
    "ASTAnalyzerPlugin",
    "IROptimizerPlugin"
] 