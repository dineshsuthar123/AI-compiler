"""Intermediate representation components for the AI compiler."""

from compiler.ir.generator import IRGenerator
from compiler.ir.optimizer import IROptimizer
from compiler.ir.types import TypeSystem

__all__ = [
    "IRGenerator",
    "IROptimizer",
    "TypeSystem"
] 