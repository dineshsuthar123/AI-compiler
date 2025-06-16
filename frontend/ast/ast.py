from typing import List, Optional, Union
from dataclasses import dataclass

@dataclass
class Node:
    """Base class for all AST nodes."""
    pass

@dataclass
class Expression(Node):
    """Base class for all expressions."""
    pass

@dataclass
class Statement(Node):
    """Base class for all statements."""
    pass

@dataclass
class Declaration(Node):
    """Base class for all declarations."""
    pass

@dataclass
class Type(Node):
    """Base class for all types."""
    name: str

@dataclass
class Identifier(Expression):
    """Represents an identifier."""
    name: str

@dataclass
class Constant(Expression):
    """Represents a constant value."""
    value: Union[int, float, str]
    type: str  # 'int', 'float', 'char', 'string'

@dataclass
class BinaryOp(Expression):
    """Represents a binary operation."""
    op: str
    left: Expression
    right: Expression

@dataclass
class UnaryOp(Expression):
    """Represents a unary operation."""
    op: str
    expr: Expression

@dataclass
class FunctionCall(Expression):
    """Represents a function call."""
    name: Identifier
    args: List[Expression]

@dataclass
class CompoundStatement(Statement):
    """Represents a compound statement (block)."""
    declarations: List[Declaration]
    statements: List[Statement]

@dataclass
class IfStatement(Statement):
    """Represents an if statement."""
    condition: Expression
    if_body: Statement
    else_body: Optional[Statement] = None

@dataclass
class WhileStatement(Statement):
    """Represents a while loop."""
    condition: Expression
    body: Statement

@dataclass
class ForStatement(Statement):
    """Represents a for loop."""
    init: Optional[Union[Expression, Declaration]]
    condition: Optional[Expression]
    update: Optional[Expression]
    body: Statement

@dataclass
class VariableDeclaration(Declaration):
    """Represents a variable declaration."""
    type: Type
    name: Identifier
    init: Optional[Expression] = None

@dataclass
class FunctionDeclaration(Declaration):
    """Represents a function declaration."""
    return_type: Type
    name: Identifier
    params: List[VariableDeclaration]
    body: Optional[CompoundStatement] = None

@dataclass
class Program(Node):
    """Represents the entire program."""
    declarations: List[Declaration]

class ASTVisitor:
    """Base visitor class for traversing the AST."""
    
    def visit(self, node: Node):
        """Visit a node."""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: Node):
        """Called if no explicit visitor function exists for a node."""
        raise NotImplementedError(
            f'No visit_{type(node).__name__} method exists'
        ) 