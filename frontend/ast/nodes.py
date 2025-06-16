import logging
from dataclasses import dataclass
from typing import List, Optional, Union, Any

class Node:
    """Base class for all AST nodes."""
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Creating {self.__class__.__name__} node")
        super().__init__()
        self._validate()

    def _validate(self):
        """Validate the node's state."""
        self.logger.debug(f"Validating {self.__class__.__name__} node")
        if not hasattr(self, '__class__'):
            raise TypeError("Node must have a class")
        if not isinstance(self, Node):
            raise TypeError(f"Expected Node instance, got {type(self)}")

class Expression(Node):
    """Base class for all expressions."""
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Creating Expression node: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating Expression node: {self.__class__.__name__}")

class Statement(Node):
    """Base class for all statements."""
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Creating Statement node: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating Statement node: {self.__class__.__name__}")

class Declaration(Node):
    """Base class for all declarations."""
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Creating Declaration node: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating Declaration node: {self.__class__.__name__}")

@dataclass
class Type(Node):
    """Represents a C type."""
    name: str
    is_const: bool = False
    is_volatile: bool = False
    is_pointer: bool = False
    pointer_depth: int = 0

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating Type node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"Type name must be a string, got {type(self.name)}")
        if not isinstance(self.is_const, bool):
            raise TypeError(f"is_const must be a boolean, got {type(self.is_const)}")
        if not isinstance(self.is_volatile, bool):
            raise TypeError(f"is_volatile must be a boolean, got {type(self.is_volatile)}")
        if not isinstance(self.is_pointer, bool):
            raise TypeError(f"is_pointer must be a boolean, got {type(self.is_pointer)}")
        if not isinstance(self.pointer_depth, int):
            raise TypeError(f"pointer_depth must be an integer, got {type(self.pointer_depth)}")

@dataclass
class Identifier(Expression):
    """Represents an identifier."""
    name: str

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating Identifier node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"Identifier name must be a string, got {type(self.name)}")

@dataclass
class Literal(Expression):
    """Base class for all literal values."""
    value: Any

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating Literal node: {self.value}")
        if self.value is None:
            raise ValueError("Literal value cannot be None")

@dataclass
class IntegerLiteral(Literal):
    """Represents an integer literal."""
    value: int

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating IntegerLiteral node: {self.value}")
        if not isinstance(self.value, int):
            raise TypeError(f"IntegerLiteral value must be an integer, got {type(self.value)}")

@dataclass
class FloatLiteral(Literal):
    """Represents a floating-point literal."""
    value: float

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating FloatLiteral node: {self.value}")
        if not isinstance(self.value, float):
            raise TypeError(f"FloatLiteral value must be a float, got {type(self.value)}")

@dataclass
class StringLiteral(Literal):
    """Represents a string literal."""
    value: str

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating StringLiteral node: {self.value}")
        if not isinstance(self.value, str):
            raise TypeError(f"StringLiteral value must be a string, got {type(self.value)}")

@dataclass
class CharLiteral(Literal):
    """Represents a character literal."""
    value: str

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating CharLiteral node: {self.value}")
        if not isinstance(self.value, str) or len(self.value) != 1:
            raise TypeError(f"CharLiteral value must be a single character string, got {self.value}")

@dataclass
class BooleanLiteral(Literal):
    """Represents a boolean literal."""
    value: bool

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating BooleanLiteral node: {self.value}")
        if not isinstance(self.value, bool):
            raise TypeError(f"BooleanLiteral value must be a boolean, got {type(self.value)}")

@dataclass
class BinaryOp(Expression):
    """Represents a binary operation."""
    op: str
    left: Expression
    right: Expression

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating BinaryOp node: {self.op}")
        if not isinstance(self.op, str):
            raise TypeError(f"BinaryOp operator must be a string, got {type(self.op)}")
        if not isinstance(self.left, Expression):
            raise TypeError(f"BinaryOp left operand must be an Expression, got {type(self.left)}")
        if not isinstance(self.right, Expression):
            raise TypeError(f"BinaryOp right operand must be an Expression, got {type(self.right)}")

@dataclass
class UnaryOp(Expression):
    """Represents a unary operation."""
    op: str
    operand: Expression

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating UnaryOp node: {self.op}")
        if not isinstance(self.op, str):
            raise TypeError(f"UnaryOp operator must be a string, got {type(self.op)}")
        if not isinstance(self.operand, Expression):
            raise TypeError(f"UnaryOp operand must be an Expression, got {type(self.operand)}")

@dataclass
class FunctionCall(Expression):
    """Represents a function call."""
    function: Expression
    arguments: List[Expression]

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating FunctionCall node: {self.function}")
        if not isinstance(self.function, Expression):
            raise TypeError(f"FunctionCall function must be an Expression, got {type(self.function)}")
        if not isinstance(self.arguments, list):
            raise TypeError(f"FunctionCall arguments must be a list, got {type(self.arguments)}")
        for arg in self.arguments:
            if not isinstance(arg, Expression):
                raise TypeError(f"FunctionCall argument must be an Expression, got {type(arg)}")

@dataclass
class VariableDecl(Declaration):
    """Represents a variable declaration."""
    name: str
    type: Type
    init: Optional[Expression] = None

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating VariableDecl node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"VariableDecl name must be a string, got {type(self.name)}")
        if not isinstance(self.type, Type):
            raise TypeError(f"VariableDecl type must be a Type, got {type(self.type)}")
        if self.init is not None and not isinstance(self.init, Expression):
            raise TypeError(f"VariableDecl init must be an Expression or None, got {type(self.init)}")

@dataclass
class Parameter(Declaration):
    """Represents a function parameter."""
    name: str
    type: Type

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating Parameter node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"Parameter name must be a string, got {type(self.name)}")
        if not isinstance(self.type, Type):
            raise TypeError(f"Parameter type must be a Type, got {type(self.type)}")

@dataclass
class FunctionDecl(Declaration):
    """Represents a function declaration."""
    name: str
    return_type: Type
    parameters: List[Parameter]
    body: Optional['CompoundStmt'] = None

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating FunctionDecl node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"FunctionDecl name must be a string, got {type(self.name)}")
        if not isinstance(self.return_type, Type):
            raise TypeError(f"FunctionDecl return_type must be a Type, got {type(self.return_type)}")
        if not isinstance(self.parameters, list):
            raise TypeError(f"FunctionDecl parameters must be a list, got {type(self.parameters)}")
        for param in self.parameters:
            if not isinstance(param, Parameter):
                raise TypeError(f"FunctionDecl parameter must be a Parameter, got {type(param)}")
        if self.body is not None and not isinstance(self.body, CompoundStmt):
            raise TypeError(f"FunctionDecl body must be a CompoundStmt or None, got {type(self.body)}")

@dataclass
class ReturnStmt(Statement):
    """Represents a return statement."""
    value: Optional[Expression] = None

    def _validate(self):
        super()._validate()
        self.logger.debug("Validating ReturnStmt node")
        if self.value is not None and not isinstance(self.value, Expression):
            raise TypeError(f"ReturnStmt value must be an Expression or None, got {type(self.value)}")

@dataclass
class ExpressionStmt(Statement):
    """Represents an expression statement."""
    expr: Expression

    def _validate(self):
        super()._validate()
        self.logger.debug("Validating ExpressionStmt node")
        if not isinstance(self.expr, Expression):
            raise TypeError(f"ExpressionStmt expr must be an Expression, got {type(self.expr)}")

@dataclass
class CompoundStmt(Statement):
    """Represents a compound statement (block)."""
    statements: List[Union[Statement, Declaration]]

    def _validate(self):
        super()._validate()
        self.logger.debug("Validating CompoundStmt node")
        if not isinstance(self.statements, list):
            raise TypeError(f"CompoundStmt statements must be a list, got {type(self.statements)}")
        for stmt in self.statements:
            if not isinstance(stmt, (Statement, Declaration)):
                raise TypeError(f"CompoundStmt statement must be a Statement or Declaration, got {type(stmt)}")

@dataclass
class IfStmt(Statement):
    """Represents an if statement."""
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement] = None

    def _validate(self):
        super()._validate()
        self.logger.debug("Validating IfStmt node")
        if not isinstance(self.condition, Expression):
            raise TypeError(f"IfStmt condition must be an Expression, got {type(self.condition)}")
        if not isinstance(self.then_branch, Statement):
            raise TypeError(f"IfStmt then_branch must be a Statement, got {type(self.then_branch)}")
        if self.else_branch is not None and not isinstance(self.else_branch, Statement):
            raise TypeError(f"IfStmt else_branch must be a Statement or None, got {type(self.else_branch)}")

@dataclass
class WhileStmt(Statement):
    """Represents a while statement."""
    condition: Expression
    body: Statement

    def _validate(self):
        super()._validate()
        self.logger.debug("Validating WhileStmt node")
        if not isinstance(self.condition, Expression):
            raise TypeError(f"WhileStmt condition must be an Expression, got {type(self.condition)}")
        if not isinstance(self.body, Statement):
            raise TypeError(f"WhileStmt body must be a Statement, got {type(self.body)}")

@dataclass
class ForStmt(Statement):
    """Represents a for statement."""
    init: Optional[Union[Expression, Declaration]]
    condition: Optional[Expression]
    increment: Optional[Expression]
    body: Statement

    def _validate(self):
        super()._validate()
        self.logger.debug("Validating ForStmt node")
        if self.init is not None and not isinstance(self.init, (Expression, Declaration)):
            raise TypeError(f"ForStmt init must be an Expression, Declaration, or None, got {type(self.init)}")
        if self.condition is not None and not isinstance(self.condition, Expression):
            raise TypeError(f"ForStmt condition must be an Expression or None, got {type(self.condition)}")
        if self.increment is not None and not isinstance(self.increment, Expression):
            raise TypeError(f"ForStmt increment must be an Expression or None, got {type(self.increment)}")
        if not isinstance(self.body, Statement):
            raise TypeError(f"ForStmt body must be a Statement, got {type(self.body)}")

@dataclass
class TranslationUnit(Node):
    """Represents a complete C source file."""
    declarations: List[Declaration]

    def _validate(self):
        super()._validate()
        self.logger.debug("Validating TranslationUnit node")
        if not isinstance(self.declarations, list):
            raise TypeError(f"TranslationUnit declarations must be a list, got {type(self.declarations)}")
        for decl in self.declarations:
            if not isinstance(decl, Declaration):
                raise TypeError(f"TranslationUnit declaration must be a Declaration, got {type(decl)}")

@dataclass
class StructDecl(Declaration):
    """Represents a struct declaration."""
    name: str
    fields: List[VariableDecl]

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating StructDecl node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"StructDecl name must be a string, got {type(self.name)}")
        if not isinstance(self.fields, list):
            raise TypeError(f"StructDecl fields must be a list, got {type(self.fields)}")
        for field in self.fields:
            if not isinstance(field, VariableDecl):
                raise TypeError(f"StructDecl field must be a VariableDecl, got {type(field)}")

@dataclass
class MemberAccess(Expression):
    """Represents member access in a struct."""
    base: Expression
    member: str

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating MemberAccess node: {self.member}")
        if not isinstance(self.member, str):
            raise TypeError(f"MemberAccess member must be a string, got {type(self.member)}")

@dataclass
class UnionDecl(Declaration):
    """Represents a union declaration."""
    name: str
    fields: List[VariableDecl]

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating UnionDecl node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"UnionDecl name must be a string, got {type(self.name)}")
        if not isinstance(self.fields, list):
            raise TypeError(f"UnionDecl fields must be a list, got {type(self.fields)}")
        for field in self.fields:
            if not isinstance(field, VariableDecl):
                raise TypeError(f"UnionDecl field must be a VariableDecl, got {type(field)}")

@dataclass
class EnumDecl(Declaration):
    """Represents an enum declaration."""
    name: str
    values: List[str]

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating EnumDecl node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"EnumDecl name must be a string, got {type(self.name)}")
        if not isinstance(self.values, list):
            raise TypeError(f"EnumDecl values must be a list, got {type(self.values)}")
        for value in self.values:
            if not isinstance(value, str):
                raise TypeError(f"EnumDecl value must be a string, got {type(value)}")

@dataclass
class TypedefDecl(Declaration):
    """Represents a typedef declaration."""
    name: str
    type: Type

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating TypedefDecl node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"TypedefDecl name must be a string, got {type(self.name)}")
        if not isinstance(self.type, Type):
            raise TypeError(f"TypedefDecl type must be a Type, got {type(self.type)}")

@dataclass
class ArrayDecl(Declaration):
    """Represents an array declaration."""
    name: str
    type: Type
    size: int

    def _validate(self):
        super()._validate()
        self.logger.debug(f"Validating ArrayDecl node: {self.name}")
        if not isinstance(self.name, str):
            raise TypeError(f"ArrayDecl name must be a string, got {type(self.name)}")
        if not isinstance(self.type, Type):
            raise TypeError(f"ArrayDecl type must be a Type, got {type(self.type)}")
        if not isinstance(self.size, int):
            raise TypeError(f"ArrayDecl size must be an integer, got {type(self.size)}")

@dataclass
class FunctionPointer(Expression):
    """Represents a function pointer."""
    return_type: Type
    param_types: List[Type]

    def _validate(self):
        super()._validate()
        self.logger.debug("Validating FunctionPointer node")
        if not isinstance(self.return_type, Type):
            raise TypeError(f"FunctionPointer return_type must be a Type, got {type(self.return_type)}")
        if not isinstance(self.param_types, list):
            raise TypeError(f"FunctionPointer param_types must be a list, got {type(self.param_types)}")
        for param_type in self.param_types:
            if not isinstance(param_type, Type):
                raise TypeError(f"FunctionPointer param_type must be a Type, got {type(param_type)}")