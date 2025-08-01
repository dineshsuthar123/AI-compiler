from typing import Any, Dict, List, Optional, Union
import logging
from antlr4 import *
from ..grammar.CParser import CParser as AntlrCParser
from ..grammar.CLexer import CLexer
from ..grammar.CListener import CListener
from ..ast.nodes import *

class ASTBuilder(CListener):
    """Builds AST from ANTLR parse tree."""
    
    def __init__(self):
        self.ast = None
        self.current_node = None
        self.node_stack = []
        self.expr_stack = []
        self.logger = logging.getLogger(__name__)
    
    def safe_pop(self, stack):
        if stack:
            return stack.pop()
        return None
    
    def warn(self, msg):
        print(f"[AI-Compiler WARNING] {msg}")

    def enterCompilationUnit(self, ctx):
        """Enter a parse tree produced by CParser.compilationUnit."""
        declarations = []
        self.current_node = TranslationUnit(declarations=declarations)
        self.ast = self.current_node
    
    def exitCompilationUnit(self, ctx):
        """Exit a parse tree produced by CParser.compilationUnit."""
        pass
    
    def enterFunctionDefinition(self, ctx):
        """Enter a parse tree produced by CParser.functionDefinition."""
        # Create a new function declaration node
        func_decl = FunctionDecl(
            name='',  # Will be filled by declarator
            return_type=None,  # Will be filled by declaration specifiers
            parameters=[],
            body=None
        )
        self.node_stack.append(self.current_node)
        self.current_node = func_decl
        
        if isinstance(self.node_stack[-1], TranslationUnit):
            self.node_stack[-1].declarations.append(func_decl)
    
    def exitFunctionDefinition(self, ctx):
        """Exit a parse tree produced by CParser.functionDefinition."""
        self.current_node = self.safe_pop(self.node_stack)
    
    def enterDeclarationSpecifiers(self, ctx):
        """Enter a parse tree produced by CParser.declarationSpecifiers."""
        # For now, just get the first type specifier
        for child in ctx.getChildren():
            if isinstance(child, AntlrCParser.TypeSpecifierContext):
                type_name = child.getText()
                if isinstance(self.current_node, FunctionDecl):
                    self.current_node.return_type = Type(name=type_name)
                break
    
    def enterDeclarator(self, ctx):
        """Enter a parse tree produced by CParser.declarator."""
        # Improved pointer type handling
        pointer_depth = ctx.getText().count('*')
        is_pointer = pointer_depth > 0
        # Set pointer info on current node if it's a variable or parameter
        if isinstance(self.current_node, (VariableDecl, Parameter)):
            self.current_node.type.is_pointer = is_pointer
            self.current_node.type.pointer_depth = pointer_depth
        # No warning needed; pointer types are now supported
    
    def exitDeclarator(self, ctx):
        # Handle array declarations
        if ctx.getChildCount() >= 4 and ctx.getChild(1).getText() == '[':
            # e.g., int a[10];
            var_name = ctx.Identifier().getText()
            size_text = ctx.getChild(2).getText()
            try:
                size = int(size_text)
            except Exception:
                size = 0
            array_decl = ArrayDecl(name=var_name, type=Type(name='int'), size=size)
            if isinstance(self.current_node, CompoundStmt):
                self.current_node.statements.append(array_decl)
    
    def enterDirectDeclarator(self, ctx):
        """Enter a parse tree produced by CParser.directDeclarator."""
        if ctx.Identifier():
            if isinstance(self.current_node, FunctionDecl):
                # Only set function name if it's not already set
                if not self.current_node.name:
                    self.current_node.name = ctx.Identifier().getText()
            elif isinstance(self.current_node, Parameter):
                self.current_node.name = ctx.Identifier().getText()
        elif ctx.declarator():
            # Handle nested declarator
            if isinstance(self.current_node, FunctionDecl):
                decl = ctx.declarator()
                if decl.directDeclarator() and decl.directDeclarator().Identifier():
                    # Only set function name if it's not already set
                    if not self.current_node.name:
                        self.current_node.name = decl.directDeclarator().Identifier().getText()
    
    def enterParameterDeclaration(self, ctx):
        """Enter a parse tree produced by CParser.parameterDeclaration."""
        param_type = Type(name='int')  # Default to int for now
        param = Parameter(name='', type=param_type)
        # Get type from declaration specifiers
        for child in ctx.declarationSpecifiers().getChildren():
            if isinstance(child, AntlrCParser.TypeSpecifierContext):
                type_name = child.getText().replace('*', '').strip()
                pointer_depth = child.getText().count('*')
                is_pointer = pointer_depth > 0
                param.type = Type(name=type_name, is_pointer=is_pointer, pointer_depth=pointer_depth)
                break
        # Get name from declarator if present
        if ctx.declarator():
            direct_decl = ctx.declarator().directDeclarator()
            if direct_decl and direct_decl.Identifier():
                param.name = direct_decl.Identifier().getText()
            # Detect pointer in declarator (e.g., int *a)
            pointer_depth = ctx.declarator().getText().count('*')
            if pointer_depth > 0:
                param.type.is_pointer = True
                param.type.pointer_depth = pointer_depth
        if isinstance(self.current_node, FunctionDecl):
            self.current_node.parameters.append(param)
    
    def enterCompoundStatement(self, ctx):
        """Enter a parse tree produced by CParser.compoundStatement."""
        print("=== ENTERING COMPOUND STATEMENT ===")
        compound = CompoundStmt(statements=[])
        if isinstance(self.current_node, FunctionDecl):
            self.current_node.body = compound
        elif isinstance(self.current_node, IfStmt):
            # If we're in an if statement, check if this compound statement is for the then or else branch
            parent = ctx.parentCtx
            if hasattr(parent, 'statement') and parent.statement(0) == ctx:
                # This is the then branch
                self.current_node.then_branch = compound
            elif hasattr(parent, 'statement') and parent.statement(1) == ctx:
                # This is the else branch
                self.current_node.else_branch = compound
        self.node_stack.append(self.current_node)
        self.current_node = compound
        print(f"Set current_node to CompoundStmt, node_stack length: {len(self.node_stack)}")    
    def exitCompoundStatement(self, ctx):
        """Exit a parse tree produced by CParser.compoundStatement."""
        self.current_node = self.safe_pop(self.node_stack)
    
    def enterDeclaration(self, ctx):
        """Enter a parse tree produced by CParser.declaration."""
        print(f"=== ENTERING DECLARATION: {ctx.getText()} ===")
        
        # Get type from declaration specifiers
        type_name = 'int'  # Default to int
        pointer_depth = 0
        for child in ctx.declarationSpecifiers().getChildren():
            if isinstance(child, AntlrCParser.TypeSpecifierContext):
                type_spec_text = child.getText()
                print(f"Found type specifier: {type_spec_text}")
                # Handle struct declarations
                if type_spec_text.startswith('struct'):
                    type_name = type_spec_text  # e.g., "structPoint" or "struct Point"
                else:
                    type_name = type_spec_text.replace('*', '').strip()
                pointer_depth = type_spec_text.count('*')
                break        
        print(f"Determined type name: {type_name}")
        
        # Check if there's an initDeclaratorList
        has_init_decl_list = ctx.initDeclaratorList() is not None
        print(f"Has initDeclaratorList: {has_init_decl_list}")
        if ctx.initDeclaratorList():
            print(f"initDeclaratorList text: {ctx.initDeclaratorList().getText()}")
        
        # Process each declarator
        if ctx.initDeclaratorList():
            print(f"Found initDeclaratorList with {len(ctx.initDeclaratorList().initDeclarator())} declarators")
            for init_decl in ctx.initDeclaratorList().initDeclarator():
                decl = init_decl.declarator()
                if decl and decl.directDeclarator() and decl.directDeclarator().Identifier():
                    var_name = decl.directDeclarator().Identifier().getText()
                    print(f"Creating variable: {var_name} of type {type_name}")
                    var_decl = VariableDecl(
                        name=var_name,
                        type=Type(name=type_name, is_pointer=(pointer_depth > 0), pointer_depth=pointer_depth),
                        init=None
                    )
                    
                    # Handle initializer if present
                    if init_decl.initializer():
                        self.node_stack.append(var_decl)
                        # The initializer will be processed in enterInitializer
                    
                    if isinstance(self.current_node, CompoundStmt):
                        self.current_node.statements.append(var_decl)
                        print(f"Added variable declaration: {var_name} of type {type_name} to CompoundStmt")
                    else:
                        print(f"Current node is not CompoundStmt, it's: {type(self.current_node)}")
        else:
            # Handle declarations without initDeclaratorList (like pure struct declarations)
            # This case is handled by struct parsing methods
            print(f"Declaration without initDeclaratorList: {type_name}")
    
    def enterInitializer(self, ctx):
        """Enter a parse tree produced by CParser.initializer."""
        if ctx.assignmentExpression():
            self.expr_stack.append([])
    
    def exitInitializer(self, ctx):
        """Exit a parse tree produced by CParser.initializer."""
        if ctx.assignmentExpression():
            expr = self.safe_pop(self.expr_stack)
            if expr and isinstance(expr, list) and expr:
                expr = expr[-1]
            if self.node_stack and isinstance(self.node_stack[-1], VariableDecl):
                var_decl = self.safe_pop(self.node_stack)
                var_decl.init = expr
    
    def enterReturnStatement(self, ctx):
        """Enter a parse tree produced by CParser.returnStatement."""
        print(f"Entering return statement: {ctx.getText()}")
        # Create a new stack frame for the return expression
        self.expr_stack.append([])
    
    def exitReturnStatement(self, ctx):
        """Exit a parse tree produced by CParser.returnStatement."""
        print(f"Exiting return statement: {ctx.getText()}")
        if ctx.expression():  # Only process if there's an expression
            expr_list = self.safe_pop(self.expr_stack)
            expr = expr_list[-1] if expr_list and isinstance(expr_list, list) and expr_list else None
            print(f"Return expression: {expr}")
            if expr:
                return_stmt = ReturnStmt(expr)
                if isinstance(self.current_node, CompoundStmt):
                    print(f"Adding return statement to compound: {return_stmt}")
                    self.current_node.statements.append(return_stmt)
                    print(f"Current compound statements: {self.current_node.statements}")
        else:
            return_stmt = ReturnStmt(None)
            if isinstance(self.current_node, CompoundStmt):
                self.current_node.statements.append(return_stmt)
    
    def enterExpression(self, ctx):
        """Enter a parse tree produced by CParser.expression."""
        print(f"Entering expression: {ctx.getText()}")
        self.expr_stack.append([])
    
    def exitExpression(self, ctx):
        """Exit a parse tree produced by CParser.expression."""
        print(f"Exiting expression: {ctx.getText()}")
        if self.expr_stack:
            if len(ctx.children) > 1:
                exprs = []
                while self.expr_stack[-1]:
                    exprs.insert(0, self.expr_stack[-1].pop())
                if len(exprs) >= 3:
                    left = exprs[0]
                    op = exprs[1]
                    right = exprs[2]
                    binary_op = BinaryOp(op=op, left=left, right=right)
                    if len(self.expr_stack) > 1:
                        self.expr_stack[-2].append(binary_op)
                    else:
                        self.expr_stack[-1].append(binary_op)
            elif self.expr_stack[-1]:
                expr = self.expr_stack[-1].pop()
                if len(self.expr_stack) > 1:
                    self.expr_stack[-2].append(expr)
                else:
                    self.expr_stack[-1].append(expr)
            self.safe_pop(self.expr_stack)
        print(f"Expression stack after exit: {self.expr_stack}")
    
    def enterPrimaryExpression(self, ctx):
        """Enter a parse tree produced by CParser.primaryExpression."""
        print(f"Entering primary expression: {ctx.getText()}")
        text = ctx.getText()
        if ctx.Identifier():
            # Handle identifier
            name = ctx.Identifier().getText()
            print(f"Found identifier: {name}")
            identifier = Identifier(name=name)
            print(f"Added identifier to stack: {identifier}")
            if self.expr_stack:
                self.expr_stack[-1].append(identifier)
                print(f"Current expression stack: {self.expr_stack}")
        elif ctx.Constant():
            # Handle constant (both integers and floating-point)
            constant_text = ctx.Constant().getText()
            print(f"Found constant: {constant_text}")
              # Try to determine if it's a float or int
            if '.' in constant_text or 'e' in constant_text.lower() or 'f' in constant_text.lower():
                # It's a floating-point number
                value = float(constant_text.rstrip('fF'))  # Remove 'f' or 'F' suffix if present
                
                # Determine precision based on suffix
                if constant_text.lower().endswith('f'):
                    # Single precision float
                    print(f"Creating FloatLiteral for: {constant_text}")
                    literal = FloatLiteral(value=value)
                else:
                    # Default to double precision for literals without 'f' suffix
                    print(f"Creating DoubleLiteral for: {constant_text}")
                    literal = DoubleLiteral(value=value)
            else:
                # It's an integer
                value = int(constant_text)
                literal = IntegerLiteral(value=value)
            
            print(f"Added literal to stack: {literal}")
            if self.expr_stack:
                self.expr_stack[-1].append(literal)
                print(f"Current expression stack: {self.expr_stack}")
        elif ctx.StringLiteral():
            # Handle string literal
            value = ctx.StringLiteral().getText()
            # Remove quotes
            value = value[1:-1]  # Remove first and last quote
            print(f"Found string literal: {value}")
            # Create a StringLiteral
            literal = StringLiteral(value=value)
            print(f"Added string literal to stack: {literal}")
            if self.expr_stack:
                self.expr_stack[-1].append(literal)
                print(f"Current expression stack: {self.expr_stack}")
    
    def exitPrimaryExpression(self, ctx):
        """Exit a parse tree produced by CParser.primaryExpression."""
        print(f"Exiting primary expression: {ctx.getText()}")
        print(f"Current expression stack: {self.expr_stack}")
    
    def enterAdditiveExpression(self, ctx):
        """Enter a parse tree produced by CParser.additiveExpression."""
        print(f"Entering additive expression: {ctx.getText()}")
        if not self.expr_stack:
            self.expr_stack.append([])
    
    def exitAdditiveExpression(self, ctx):
        """Exit a parse tree produced by CParser.additiveExpression."""
        if len(ctx.children) > 1:  # Binary operation
            op = ctx.children[1].getText()
            if op in ['+', '-']:
                if len(self.expr_stack[-1]) >= 2:
                    right = self.expr_stack[-1].pop()
                    left = self.expr_stack[-1].pop()
                    binary_op = BinaryOp(op=op, left=left, right=right)
                    print(f"Created additive op: {binary_op}")
                    self.expr_stack[-1].append(binary_op)
    
    def enterMultiplicativeExpression(self, ctx):
        """Enter a parse tree produced by CParser.multiplicativeExpression."""
        self.expr_stack.append([])
    
    def exitMultiplicativeExpression(self, ctx):
        """Exit a parse tree produced by CParser.multiplicativeExpression."""
        if len(ctx.children) > 1:  # Binary operation
            op = ctx.children[1].getText()
            if op in ['*', '/', '%']:
                if len(self.expr_stack[-1]) >= 2:
                    right = self.expr_stack[-1].pop()
                    left = self.expr_stack[-1].pop()
                    # Create binary operation
                    binary_op = BinaryOp(op=op, left=left, right=right)
                    print(f"Created multiplicative op: {binary_op}")
                    if len(self.expr_stack) > 1:
                        self.expr_stack[-2].append(binary_op)
                    else:
                        self.expr_stack[-1].append(binary_op)
        elif self.expr_stack[-1]:
            # Single expression, move it up one level
            expr = self.expr_stack[-1].pop()
            if len(self.expr_stack) > 1:
                self.expr_stack[-2].append(expr)
            else:
                self.expr_stack[-1].append(expr)
        self.safe_pop(self.expr_stack)
    
    def enterAssignmentExpression(self, ctx):
        """Enter a parse tree produced by CParser.assignmentExpression."""
        if not self.expr_stack:
            self.expr_stack.append([])
    
    def exitAssignmentExpression(self, ctx):
        """Exit a parse tree produced by CParser.assignmentExpression."""
        if len(ctx.children) == 3:  # Assignment operation
            op = ctx.children[1].getText()
            if self.expr_stack and len(self.expr_stack[-1]) >= 2:
                right = self.expr_stack[-1].pop()
                left = self.expr_stack[-1].pop()
                self.expr_stack[-1].append(BinaryOp(op=op, left=left, right=right))
        elif len(ctx.children) == 1:  # Just a conditional expression
            # The expression is already on the stack
            pass
    
    def enterExpressionStatement(self, ctx):
        """Enter a parse tree produced by CParser.expressionStatement."""
        if ctx.expression():
            self.expr_stack.append([])
    
    def exitExpressionStatement(self, ctx):
        """Exit a parse tree produced by CParser.expressionStatement."""
        if ctx.expression():
            expr = self.safe_pop(self.expr_stack)
            expr_stmt = ExpressionStmt(expr=expr[-1] if expr and isinstance(expr, list) and expr else None)
            if isinstance(self.current_node, CompoundStmt):
                self.current_node.statements.append(expr_stmt)
    
    def enterPostfixExpression(self, ctx):
        """Enter a parse tree produced by CParser.postfixExpression."""
        self.expr_stack.append([])
    
    def exitPostfixExpression(self, ctx):
        """Exit a parse tree produced by CParser.postfixExpression."""
        if len(ctx.children) > 1:
            op = ctx.children[1].getText()
            
            if op == '(':  # This is a function call
                exprs = []
                while self.expr_stack[-1]:
                    exprs.insert(0, self.expr_stack[-1].pop())
                if exprs:
                    func = exprs[0]
                    args = []
                    if len(exprs) > 1:
                        args.extend(exprs[1:])
                    # Only warn and skip for malloc/free, not for user functions like swap
                    if isinstance(func, Identifier) and func.name in ("malloc", "free"):
                        self.warn(f"Function '{func.name}' is not fully supported yet. Skipping call.")
                        return
                    # For all other functions, including swap, create the FunctionCall node
                    func_call = FunctionCall(function=func, arguments=args)
                    print(f"Created function call: {func_call}")
                    if len(self.expr_stack) > 1:
                        self.expr_stack[-2].append(func_call)
                    else:
                        self.expr_stack[-1].append(func_call)
            
            elif op == '.' or op == '->':  # Member access
                if len(ctx.children) >= 3:  # object, '.', member
                    exprs = []
                    while self.expr_stack[-1]:
                        exprs.insert(0, self.expr_stack[-1].pop())
                    
                    if exprs:
                        object_expr = exprs[0]  # The object (e.g., 'p')
                        member_name = ctx.children[2].getText()  # The member (e.g., 'x')
                          # Create member access node
                        member_access = MemberAccess(
                            base=object_expr,
                            member=member_name
                        )
                        print(f"Created member access: {member_access}")
                        
                        if len(self.expr_stack) > 1:
                            self.expr_stack[-2].append(member_access)
                        else:
                            self.expr_stack[-1].append(member_access)
                    
            # Handle struct pointer access: a->b
            if ctx.getChildCount() == 3 and ctx.getChild(1).getText() == '->':
                base_expr = self.safe_pop(self.expr_stack)
                member_name = ctx.getChild(2).getText()
                struct_ptr_access = StructPointerAccess(base=base_expr, member=member_name)
                if self.expr_stack:
                    self.expr_stack[-1].append(struct_ptr_access)
            
        elif self.expr_stack[-1]:
            expr = self.expr_stack[-1].pop()
            if len(self.expr_stack) > 1:
                self.expr_stack[-2].append(expr)
            else:
                self.expr_stack[-1].append(expr)
        self.safe_pop(self.expr_stack)
    
    def enterArgumentExpressionList(self, ctx):
        """Enter a parse tree produced by CParser.argumentExpressionList."""
        if not self.expr_stack:
            self.expr_stack.append([])
    
    def exitArgumentExpressionList(self, ctx):
        """Exit a parse tree produced by CParser.argumentExpressionList."""
        if len(ctx.children) > 1:  # Multiple arguments
            args = []
            while self.expr_stack[-1]:
                args.insert(0, self.expr_stack[-1].pop())
            # Put arguments back on stack in correct order
            self.expr_stack[-1].extend(args)

    def enterJumpStatement(self, ctx):
        """Enter a parse tree produced by CParser.jumpStatement."""
        print(f"Entering jump statement: {ctx.getText()}")
        if ctx.getChild(0).getText() == 'return':
            # Create a new stack frame for the return expression
            self.expr_stack.append([])
    
    def exitJumpStatement(self, ctx):
        """Exit a parse tree produced by CParser.jumpStatement."""
        print(f"Exiting jump statement: {ctx.getText()}")
        if ctx.getChild(0).getText() == 'return':
            if ctx.expression():  # Only process if there's an expression
                expr_list = self.safe_pop(self.expr_stack)
                expr = expr_list[-1] if expr_list and isinstance(expr_list, list) and expr_list else None
                print(f"Return expression: {expr}")
                if expr:
                    return_stmt = ReturnStmt(value=expr)
                    if isinstance(self.current_node, CompoundStmt):
                        print(f"Adding return statement to compound: {return_stmt}")
                        self.current_node.statements.append(return_stmt)
                        print(f"Current compound statements: {self.current_node.statements}")
            else:
                # Handle void return
                return_stmt = ReturnStmt(value=None)
                if isinstance(self.current_node, CompoundStmt):
                    self.current_node.statements.append(return_stmt)

    def exitRelationalExpression(self, ctx):
        """Exit a parse tree produced by CParser.relationalExpression."""
        if len(ctx.children) > 1:  # Binary operation
            op = ctx.children[1].getText()
            if op in ['<', '>', '<=', '>=']:
                if len(self.expr_stack[-1]) >= 2:
                    right = self.expr_stack[-1].pop()
                    left = self.expr_stack[-1].pop()
                    binary_op = BinaryOp(op=op, left=left, right=right)
                    print(f"Created relational op: {binary_op}")
                    self.expr_stack[-1].append(binary_op)

    def enterIfStatement(self, ctx):
        """Enter a parse tree produced by CParser.ifStatement."""
        if not self.expr_stack:
            self.expr_stack.append([])
    
    def exitIfStatement(self, ctx):
        """Exit a parse tree produced by CParser.ifStatement."""
        # Get condition from expression stack
        if self.expr_stack and self.expr_stack[-1]:
            condition = self.safe_pop(self.expr_stack)
            condition = condition[-1] if condition and isinstance(condition, list) and condition else None
            # Get then branch
            then_branch = None
            if ctx.statement(0):
                if isinstance(self.current_node, CompoundStmt) and self.current_node.statements:
                    then_branch = self.current_node.statements.pop(0)
                else:
                    then_branch = self.current_node if isinstance(self.current_node, Statement) else None
            # Get else branch
            else_branch = None
            if len(ctx.statement()) > 1:
                if isinstance(self.current_node, CompoundStmt) and self.current_node.statements:
                    else_branch = self.current_node.statements.pop(0)
                else:
                    else_branch = self.current_node if isinstance(self.current_node, Statement) else None
            # Create if statement
            if_stmt = IfStmt(condition=condition, then_branch=then_branch, else_branch=else_branch)
            # Add to current compound statement
            if isinstance(self.current_node, CompoundStmt):
                self.current_node.statements.append(if_stmt)
            elif self.node_stack and isinstance(self.node_stack[-1], CompoundStmt):
                self.node_stack[-1].statements.append(if_stmt)

    def enterSelectionStatement(self, ctx):
        """Enter a parse tree produced by CParser.selectionStatement."""
        # Create a new stack frame for the condition expression
        self.expr_stack.append([])
        
        # Create an if statement node with empty branches
        if_stmt = IfStmt(
            condition=None,  # Will be filled by condition expression
            then_branch=CompoundStmt(statements=[]),
            else_branch=None
        )
        
        # Push the current node onto the stack and set the if statement as current
        self.node_stack.append(self.current_node)
        self.current_node = if_stmt
    
    def exitSelectionStatement(self, ctx):
        """Exit a parse tree produced by CParser.selectionStatement."""
        # Get the condition from the expression stack
        condition = self.safe_pop(self.expr_stack)
        condition = condition[-1] if condition and isinstance(condition, list) and condition else None
        
        # Get then branch
        then_branch = None
        if ctx.statement(0):  # First statement is then branch
            if isinstance(self.current_node, CompoundStmt):
                # Get all statements for the then branch
                then_stmts = []
                while self.current_node.statements:
                    stmt = self.current_node.statements.pop(0)
                    then_stmts.append(stmt)
                
                if len(then_stmts) == 1:
                    then_branch = then_stmts[0]
                else:
                    then_branch = CompoundStmt(statements=then_stmts)
        
        # Get else branch
        else_branch = None
        if len(ctx.statement()) > 1:  # Second statement is else branch
            if isinstance(self.current_node, CompoundStmt):
                # Get all statements for the else branch
                else_stmts = []
                while self.current_node.statements:
                    stmt = self.current_node.statements.pop(0)
                    else_stmts.append(stmt)
                
                if len(else_stmts) == 1:
                    else_branch = else_stmts[0]
                else:
                    else_branch = CompoundStmt(statements=else_stmts)
        
        # Create if statement
        if_stmt = IfStmt(condition=condition, then_branch=then_branch, else_branch=else_branch)
        
        # Restore the parent node from the stack
        self.current_node = self.safe_pop(self.node_stack)
        
        # Add to current compound statement
        if isinstance(self.current_node, CompoundStmt):
            self.current_node.statements.append(if_stmt)
        elif isinstance(self.current_node, FunctionDecl):
            self.current_node.body = CompoundStmt(statements=[if_stmt])

    def enterIterationStatement(self, ctx):
        """Enter a parse tree produced by CParser.iterationStatement."""
        # Detect for-loop with declaration in initializer
        if hasattr(ctx, 'For') and ctx.For():
            # Try to extract declaration from the for-loop initializer
            if ctx.forCondition() and ctx.forCondition().declaration():
                decl_ctx = ctx.forCondition().declaration()
                # Only handle simple int i = 0; for now
                type_name = 'int'
                for child in decl_ctx.declarationSpecifiers().getChildren():
                    if hasattr(child, 'getText'):
                        type_name = child.getText()
                        break
                if decl_ctx.initDeclaratorList():
                    for init_decl in decl_ctx.initDeclaratorList().initDeclarator():
                        decl = init_decl.declarator()
                        if decl and decl.directDeclarator() and decl.directDeclarator().Identifier():
                            var_name = decl.directDeclarator().Identifier().getText()
                            var_decl = VariableDecl(
                                name=var_name,
                                type=Type(name=type_name),
                                init=None
                            )
                            # Handle initializer if present
                            if init_decl.initializer():
                                # The initializer will be processed in enterInitializer
                                self.node_stack.append(var_decl)
                            # Set as the init of the ForStmt
                            for_stmt = ForStmt(init=var_decl, condition=None, increment=None, body=None)
                            self.node_stack.append(self.current_node)
                            self.current_node = for_stmt
                            return
        self.warn("For-loops with declarations are not fully supported yet. Loop body will be skipped if unsupported.")
        pass

    def exitFunctionCall(self, ctx):
        """Exit a parse tree produced by CParser.functionCall."""
        exprs = []
        while self.expr_stack[-1]:
            exprs.insert(0, self.expr_stack[-1].pop())
        if exprs:
            func = exprs[0]
            args = exprs[1:] if len(exprs) > 1 else []
            func_call = FunctionCall(function=func, arguments=args)
            print(f"Created function call: {func_call}")
            self.expr_stack[-1].append(func_call)

    def enterStatement(self, ctx):
        """Enter a parse tree produced by CParser.statement."""
        parent = ctx.parentCtx
        
        # Check if this is a then or else branch of an if statement
        if hasattr(parent, 'statement'):
            # Get all statement children
            children = parent.getChildren()
            statements = []
            
            def process_child(child):
                if isinstance(child, list):
                    for item in child:
                        process_child(item)
                elif hasattr(child, 'getRuleIndex'):
                    try:
                        if child.getRuleIndex() == parent.statement().getRuleIndex():
                            statements.append(child)
                    except:
                        pass
            
            process_child(children)
            
            if statements and statements[0] == ctx:
                # This is the 'then' branch
                if isinstance(self.current_node, IfStmt):
                    self.current_node.then_branch = CompoundStmt(statements=[])
                    self.node_stack.append(self.current_node)
                    self.current_node = self.current_node.then_branch
            elif len(statements) > 1 and statements[1] == ctx:
                # This is the 'else' branch
                if isinstance(self.current_node, IfStmt):
                    self.current_node.else_branch = CompoundStmt(statements=[])
                    self.node_stack.append(self.current_node)
                    self.current_node = self.current_node.else_branch
        elif isinstance(self.current_node, CompoundStmt):
            # If we're in a compound statement, keep track of the parent
            self.node_stack.append(self.current_node)
    
    def exitStatement(self, ctx):
        """Exit a parse tree produced by CParser.statement."""
        # If we have a statement on the stack, add it to the current node
        if self.expr_stack and self.expr_stack[-1]:
            stmt = self.safe_pop(self.expr_stack)
            stmt = stmt[-1] if stmt and isinstance(stmt, list) and stmt else None
            if isinstance(self.current_node, CompoundStmt):
                self.current_node.statements.append(stmt)
          # Restore the previous node if we're in an if statement branch
        self.current_node = self.safe_pop(self.node_stack)
    
    def enterStructOrUnionSpecifier(self, ctx):
        """Enter a parse tree produced by CParser.structOrUnionSpecifier."""
        struct_name = None
        if ctx.Identifier():
            struct_name = ctx.Identifier().getText()
        
        # If this is a struct definition (has body)
        if ctx.structDeclarationList():
            # Initialize struct fields list
            self.struct_fields = []
            self.logger.debug(f"Starting struct definition: {struct_name}")
        else:
            # This is just a struct reference
            self.logger.debug(f"Struct reference: {struct_name}")
    
    def exitStructOrUnionSpecifier(self, ctx):
        """Exit a parse tree produced by CParser.structOrUnionSpecifier."""
        struct_name = None
        if ctx.Identifier():
            struct_name = ctx.Identifier().getText()
        
        # If this was a struct definition, create StructDecl node
        if ctx.structDeclarationList() and hasattr(self, 'struct_fields'):
            struct_decl = StructDecl(
                name=struct_name or f"anonymous_struct_{id(ctx)}",
                fields=self.struct_fields
            )
            
            # Add to current translation unit or compound statement
            if isinstance(self.current_node, (TranslationUnit, CompoundStmt)):
                if hasattr(self.current_node, 'statements'):
                    self.current_node.statements.append(struct_decl)
                else:
                    self.current_node.declarations.append(struct_decl)
            
            # Clean up
            delattr(self, 'struct_fields')
            self.logger.debug(f"Created struct declaration: {struct_name}")
    
    def enterStructDeclaration(self, ctx):
        """Enter a parse tree produced by CParser.structDeclaration."""
        # Get type from specifier qualifier list
        self.current_struct_type = 'int'  # Default
        for child in ctx.specifierQualifierList().getChildren():
            if hasattr(child, 'getText'):
                text = child.getText()
                if text in ['int', 'float', 'double', 'char', 'void']:
                    self.current_struct_type = text
                    break
    
    def enterStructDeclarator(self, ctx):
        """Enter a parse tree produced by CParser.structDeclarator."""
        if ctx.declarator() and ctx.declarator().directDeclarator():
            direct_decl = ctx.declarator().directDeclarator()
            if direct_decl.Identifier():
                field_name = direct_decl.Identifier().getText()
                field_decl = VariableDecl(
                    name=field_name,
                    type=Type(name=self.current_struct_type),
                    init=None
                )                
                # Add to current struct fields
                if hasattr(self, 'struct_fields'):
                    self.struct_fields.append(field_decl)
                    self.logger.debug(f"Added struct field: {field_name} of type {self.current_struct_type}")
    def enterBlockItem(self, ctx):
        """Enter a parse tree produced by CParser.blockItem."""
        print(f"=== ENTERING BLOCK ITEM: {ctx.getText()} ===")
        # Block items can be declarations or statements
        if ctx.declaration():
            print(f"Block item is a DECLARATION: {ctx.declaration().getText()}")
            # Don't manually trigger - let ANTLR's tree walking handle it
        elif ctx.statement():
            print(f"Block item is a STATEMENT: {ctx.statement().getText()}")
        else:
            print(f"Block item is UNKNOWN type")
        
    def enterBlockItemList(self, ctx):
        """Enter a parse tree produced by CParser.blockItemList."""
        print(f"=== ENTERING BLOCK ITEM LIST ===")
        if ctx.blockItem():
            print(f"Found {len(ctx.blockItem())} block items")
    
    def enterUnaryExpression(self, ctx):
        """Enter a parse tree produced by CParser.unaryExpression."""
        # All unary operators handled; push to expr_stack for all cases
        if ctx.unaryOperator() and len(ctx.children) == 2:
            self.expr_stack.append([])
    
    def exitUnaryExpression(self, ctx):
        """Exit a parse tree produced by CParser.unaryExpression."""
        # Handle increment/decrement (++/--)
        if ctx.getChildCount() == 2 and ctx.getChild(0).getText() in ('++', '--'):
            op = ctx.getChild(0).getText()
            expr = self.safe_pop(self.expr_stack)
            inc = IncrementOp(op=op, expr=expr, is_postfix=False)
            if self.expr_stack:
                self.expr_stack[-1].append(inc)
        elif ctx.getChildCount() == 2 and ctx.getChild(1).getText() in ('++', '--'):
            op = ctx.getChild(1).getText()
            expr = self.safe_pop(self.expr_stack)
            inc = IncrementOp(op=op, expr=expr, is_postfix=True)
            if self.expr_stack:
                self.expr_stack[-1].append(inc)
        # Handle all unary operators
        if ctx.unaryOperator() and len(ctx.children) == 2:
            operator_text = ctx.unaryOperator().getText()
            operand_expr = self.safe_pop(self.expr_stack)
            unary_op = UnaryOp(op=operator_text, operand=operand_expr)
            if self.expr_stack:
                self.expr_stack[-1].append(unary_op)
    
    def enterUnaryOperator(self, ctx):
        """Enter a parse tree produced by CParser.unaryOperator."""
        print(f"Entering unary operator: {ctx.getText()}")
        # No action needed - just for debugging
    
    def exitUnaryOperator(self, ctx):
        """Exit a parse tree produced by CParser.unaryOperator."""
        print(f"Exiting unary operator: {ctx.getText()}")
        # No action needed - handled in exitUnaryExpression

    def exitCastExpression(self, ctx):
        # Handle explicit casts: (type)expr
        if ctx.getChildCount() == 4 and ctx.getChild(0).getText() == '(':  # (type) expr
            type_name = ctx.getChild(1).getText()
            expr = self.safe_pop(self.expr_stack)
            cast_expr = CastExpr(target_type=Type(name=type_name), expr=expr)
            if self.expr_stack:
                self.expr_stack[-1].append(cast_expr)

    def exitConditionalExpression(self, ctx):
        # Handle ternary operator: cond ? true_expr : false_expr
        if ctx.getChildCount() == 5 and ctx.getChild(1).getText() == '?':
            cond = self.safe_pop(self.expr_stack)
            true_expr = self.safe_pop(self.expr_stack)
            false_expr = self.safe_pop(self.expr_stack)
            ternary = TernaryOp(condition=cond, true_expr=true_expr, false_expr=false_expr)
            if self.expr_stack:
                self.expr_stack[-1].append(ternary)

    def exitBitwiseExpression(self, ctx):
        # Handle bitwise ops (&, |, ^, ~, <<, >>)
        if ctx.getChildCount() == 3:
            left = self.safe_pop(self.expr_stack)
            right = self.safe_pop(self.expr_stack)
            op = ctx.getChild(1).getText()
            bitwise = BitwiseOp(op=op, left=left, right=right)
            if self.expr_stack:
                self.expr_stack[-1].append(bitwise)
        elif ctx.getChildCount() == 2 and ctx.getChild(0).getText() == '~':
            expr = self.safe_pop(self.expr_stack)
            bitwise = BitwiseOp(op='~', left=expr)
            if self.expr_stack:
                self.expr_stack[-1].append(bitwise)

    def exitAssignmentExpression(self, ctx):
        # Handle compound assignment (+=, -=, etc.)
        if ctx.getChildCount() == 3 and ctx.getChild(1).getText() in ('+=', '-=', '*=', '/=', '&=', '|=', '^=', '<<=', '>>='):
            left = self.safe_pop(self.expr_stack)
            right = self.safe_pop(self.expr_stack)
            op = ctx.getChild(1).getText()
            assign = AssignmentOp(op=op, left=left, right=right)
            if self.expr_stack:
                self.expr_stack[-1].append(assign)

    def exitSizeofExpression(self, ctx):
        # Handle sizeof(expr)
        if ctx.getChildCount() == 4 and ctx.getChild(0).getText() == 'sizeof':
            expr = self.safe_pop(self.expr_stack)
            sizeof_expr = SizeofExpr(expr=expr)
            if self.expr_stack:
                self.expr_stack[-1].append(sizeof_expr)

# === TODO: FULL C SUPPORT STUBS ===
# TODO: Support for struct/union/enum/typedef parsing
# TODO: Support for array declarations and indexing
# TODO: Support for pointer arithmetic and pointer-to-member
# TODO: Support for all C control flow (for, while, do-while, switch, goto, break, continue)
# TODO: Support for all C expressions (bitwise, logical, ternary, cast, sizeof, etc.)
# TODO: Support for function pointers and variadic functions
# TODO: Support for preprocessor directives (#include, #define, #ifdef, #ifndef, #endif)
# TODO: Support for global/static/extern variables
# TODO: Support for variable scoping and shadowing
# TODO: Support for error handling and recovery
# === END FULL C SUPPORT STUBS ===

# === STRUCT SUPPORT STUBS ===
# TODO: Parse struct declarations and add StructDecl nodes to the AST
# TODO: Parse member access expressions (a.b) and create MemberAccess nodes
# === END STRUCT SUPPORT STUBS ===

class CParser:
    """C language parser that generates AST."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the C parser.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def parse(self, source_code: str) -> TranslationUnit:
        """Parse C source code and return AST."""
        # Create lexer and parser
        input_stream = InputStream(source_code)
        lexer = CLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = AntlrCParser(token_stream)
        
        # Parse the input
        tree = parser.compilationUnit()
        
        # Build AST
        ast_builder = ASTBuilder()
        walker = ParseTreeWalker()
        walker.walk(ast_builder, tree)
        
        return ast_builder.ast
    
    def _create_lexer(self, input_stream: InputStream):
        """Create a C lexer for the input stream."""
        # TODO: Implement C lexer creation
        raise NotImplementedError
    
    def _create_parser(self, token_stream: CommonTokenStream):
        """Create a C parser for the token stream."""
        # TODO: Implement C parser creation        raise NotImplementedError
    
    def _convert_to_ast(self, parse_tree):
        """Convert ANTLR parse tree to our AST representation."""
        # TODO: Implement parse tree to AST conversion
        raise NotImplementedError

# TODO: Add support for pointer types, address-of, dereference, for-loops with declarations, malloc/free, etc.