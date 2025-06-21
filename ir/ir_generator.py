from typing import Any, Dict, Optional, List
import logging
from llvmlite import ir
from llvmlite.ir import IRBuilder
from frontend.ast.nodes import *

class IRGenerator:
    """Generates LLVM IR from AST."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the IR generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.module = ir.Module(name="main")
        self.builder = IRBuilder()
        self.function = None
        self.symbol_table: Dict[str, Any] = {}
        self.string_counter = 0
        self.printf_func = None
        self._init_module()
        self._init_builtins()
    
    def _init_module(self):
        """Initialize the LLVM module."""
        # Add target triple and data layout
        self.module.triple = "x86_64-pc-windows-msvc"
        self.module.data_layout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
    
    def _init_builtins(self):
        # Declare printf function
        printf_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        self.printf_func = ir.Function(self.module, printf_type, name="printf")
    
    def _create_string_constant(self, value: str) -> ir.Constant:
        """Create a string constant in the LLVM module."""
        # Properly escape backslashes and handle newlines
        str_val = value.replace('\\', '\\\\').replace('\n', '\\n') + "\0"
        
        # Create a global string constant
        str_type = ir.ArrayType(ir.IntType(8), len(str_val))
        str_const = ir.Constant(str_type, bytearray(str_val.encode("utf-8")))
        
        # Create a global variable for the string
        str_global = ir.GlobalVariable(self.module, str_type, ".str")
        str_global.linkage = "private"
        str_global.global_constant = True
        str_global.initializer = str_const
        
        # Return a pointer to the string
        return str_global.gep([ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
    
    def visit(self, node: Optional[Node]) -> Any:
        """Visit an AST node and generate corresponding IR.
        
        Args:
            node: The AST node to visit, or None
            
        Returns:
            The generated IR value, or None if the input node was None
            
        Raises:
            TypeError: If the node is not an AST node
            NotImplementedError: If no visitor method exists for the node type
        """
        if node is None:
            self.logger.debug("Received None node")
            return None
            
        if not isinstance(node, Node):
            self.logger.error(f"Invalid node type: {type(node)}, value: {node}")
            raise TypeError(f"Expected AST node, got {type(node)}")
            
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, None)
        if visitor is None:
            self.logger.error(f"No visitor method for node type: {node.__class__.__name__}")
            raise NotImplementedError(f"No visitor method for {node.__class__.__name__}")
            
        self.logger.debug(f"Visiting node: {node.__class__.__name__}")
        return visitor(node)
    
    def visit_TranslationUnit(self, node: TranslationUnit) -> None:
        """Generate IR for a translation unit."""
        self.logger.debug("Visiting translation unit")
        # First, declare all functions (signatures only)
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl):
                param_types = [self.visit(param.type) for param in decl.parameters]
                func_type = ir.FunctionType(self.visit(decl.return_type), param_types)
                if decl.name not in self.module.globals:
                    ir.Function(self.module, func_type, name=decl.name)
        # Then, generate bodies for all functions
        for decl in node.declarations:
            self.visit(decl)
    
    def visit_FunctionDecl(self, node: FunctionDecl) -> ir.Function:
        """Visit a function declaration node"""
        self.logger.debug(f"Visiting function declaration: {node.name}")
        # Get or create function
        param_types = [self.visit(param.type) for param in node.parameters]
        func_type = ir.FunctionType(self.visit(node.return_type), param_types)
        if node.name in self.module.globals:
            func = self.module.get_global(node.name)
        else:
            func = ir.Function(self.module, func_type, name=node.name)
        func.attributes.add('noinline')
        # Only generate body if not already generated
        if func.is_declaration:
            entry_block = func.append_basic_block('entry')
            self.builder.position_at_end(entry_block)
            old_symbol_table = self.symbol_table
            self.symbol_table = {}
            for arg, param in zip(func.args, node.parameters):
                param_type = self.visit(param.type)
                alloca = self.builder.alloca(param_type, name=f"{param.name}.1")
                self.builder.store(arg, alloca)
                self.symbol_table[param.name] = alloca
            if node.body:
                self.visit(node.body)
                if not self.builder.block.is_terminated:
                    self.builder.ret(ir.Constant(self.visit(node.return_type), 0))
            else:
                self.builder.ret(ir.Constant(self.visit(node.return_type), 0))
            self.symbol_table = old_symbol_table
        return func
    
    def visit_CompoundStmt(self, node: CompoundStmt) -> None:
        """Generate IR for a compound statement."""
        self.logger.debug("Visiting compound statement")
        for stmt in node.statements:
            if not self.builder.block.is_terminated:
                self.visit(stmt)
    
    def visit_ReturnStmt(self, node: ReturnStmt) -> None:
        """Generate IR for a return statement."""
        self.logger.debug("Visiting return statement")
        if node.value:
            ret_val = self.visit(node.value)
            self.builder.ret(ret_val)
        else:            self.builder.ret(ir.Constant(ir.IntType(32), 0))
    
    def visit_BinaryOp(self, node: BinaryOp) -> ir.Value:
        """Generate IR for a binary operation."""
        self.logger.debug(f"Visiting binary operation: {node.op}")
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if node.op == '+':
            return self.builder.add(left, right)
        elif node.op == '-':
            return self.builder.sub(left, right)
        elif node.op == '*':
            return self.builder.mul(left, right)
        elif node.op == '/':
            return self.builder.sdiv(left, right)
        elif node.op == '==':
            return self.builder.icmp_signed('==', left, right)
        elif node.op == '!=':
            return self.builder.icmp_signed('!=', left, right)
        elif node.op == '<':
            return self.builder.icmp_signed('<', left, right)
        elif node.op == '<=':
            return self.builder.icmp_signed('<=', left, right)
        elif node.op == '>':
            return self.builder.icmp_signed('>', left, right)
        elif node.op == '>=':
            return self.builder.icmp_signed('>=', left, right)
        elif node.op == '=':
            # Assignment: handle pointer, variable, and member access assignment
            if isinstance(node.left, UnaryOp) and node.left.op == '*':
                ptr = self.visit(node.left.operand)
                self.builder.store(right, ptr)
                return right
            elif isinstance(node.left, MemberAccess):
                # Handle member access assignment (e.g., p.x = 3.0)
                # Use the GEP pointer from visit_MemberAccess
                ptr = self.visit(node.left, as_pointer=True)
                
                # Perform type conversion if needed
                if hasattr(right, 'type') and hasattr(ptr.type, 'pointee'):
                    if ptr.type.pointee != right.type:
                        # Convert between float/double types
                        if isinstance(ptr.type.pointee, ir.DoubleType) and isinstance(right.type, ir.FloatType):
                            right = self.builder.fpext(right, ir.DoubleType())
                        elif isinstance(ptr.type.pointee, ir.FloatType) and isinstance(right.type, ir.DoubleType):
                            right = self.builder.fptrunc(right, ir.FloatType())
                        # Convert integer to float/double
                        elif isinstance(ptr.type.pointee, (ir.FloatType, ir.DoubleType)) and isinstance(right.type, ir.IntType):
                            right = self.builder.sitofp(right, ptr.type.pointee)
                        # Convert float/double to integer
                        elif isinstance(right.type, (ir.FloatType, ir.DoubleType)) and isinstance(ptr.type.pointee, ir.IntType):
                            right = self.builder.fptosi(right, ptr.type.pointee)
                
                self.builder.store(right, ptr)
                return right
            elif isinstance(node.left, Identifier):
                var_name = node.left.name
                ptr = self.symbol_table[var_name]
                # If the variable is a pointer, store pointer value directly
                if isinstance(ptr.type.pointee, ir.PointerType):
                    # If right is an identifier, get its pointer
                    if isinstance(node.right, Identifier):
                        right_ptr = self.visit(node.right, as_pointer=True)
                        self.builder.store(right_ptr, ptr)
                    else:
                        self.builder.store(right, ptr)
                else:
                    self.builder.store(right, ptr)
                return right
            else:
                raise ValueError("Left side of assignment must be a variable identifier, member access, or pointer dereference")
        else:
            raise ValueError(f"Unknown binary operator: {node.op}")
    
    def visit_UnaryOp(self, node: UnaryOp) -> ir.Value:
        """Generate IR for a unary operation."""
        self.logger.debug(f"Visiting unary operation: {node.op}")
        if node.op == '*':
            # Dereference: load the value pointed by operand
            ptr = self.visit(node.operand)
            return self.builder.load(ptr)
        elif node.op == '&':
            # Address-of: just return the pointer (operand must be an identifier)
            if isinstance(node.operand, Identifier):
                var_name = node.operand.name
                return self.symbol_table[var_name]
            else:
                raise ValueError("Address-of operator can only be applied to identifiers")
        elif node.op == '-':
            operand = self.visit(node.operand)
            return self.builder.neg(operand)
        elif node.op == '!':
            operand = self.visit(node.operand)
            return self.builder.not_(operand)
        else:
            raise ValueError(f"Unknown unary operator: {node.op}")
    
    def visit_Literal(self, node: Literal) -> ir.Constant:
        """Generate IR for a literal."""
        self.logger.debug(f"Visiting literal: {node.value}")
        return ir.Constant(ir.IntType(32), node.value)
    
    def visit_Identifier(self, node: Identifier, as_pointer: bool = False) -> ir.Value:
        """Generate IR for an identifier."""
        self.logger.debug(f"Visiting identifier: {node.name}")
        if node.name not in self.symbol_table:
            raise ValueError(f"Variable not found: {node.name}")
        ptr = self.symbol_table[node.name]
        if as_pointer:
            return ptr
        return self.builder.load(ptr)
    
    def visit_IfStmt(self, node: IfStmt) -> None:
        """Generate IR for an if statement."""
        self.logger.debug("Visiting if statement")
        # Visit condition
        cond_value = self.visit(node.condition)
        
        # Create blocks
        then_block = self.builder.append_basic_block('then')
        else_block = self.builder.append_basic_block('else')
        merge_block = self.builder.append_basic_block('merge')
        
        # Branch based on condition
        self.builder.cbranch(cond_value, then_block, else_block)
        
        # Generate then block
        self.builder.position_at_start(then_block)
        self.visit(node.then_branch)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)
        
        # Generate else block
        self.builder.position_at_start(else_block)
        if node.else_branch:
            self.visit(node.else_branch)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)
        
        # Continue in merge block if it's reachable
        if not (then_block.is_terminated and else_block.is_terminated):
            self.builder.position_at_start(merge_block)
        else:
            # If both branches end in return, remove the unreachable merge block
            merge_block.parent = None
    
    def visit_WhileStmt(self, node: WhileStmt) -> None:
        """Generate IR for a while statement."""
        self.logger.debug("Visiting while statement")
        # Create basic blocks
        cond_block = self.builder.append_basic_block("while.cond")
        body_block = self.builder.append_basic_block("while.body")
        end_block = self.builder.append_basic_block("while.end")
        
        # Branch to condition block
        self.builder.branch(cond_block)
        
        # Emit condition
        self.builder.position_at_end(cond_block)
        condition = self.visit(node.condition)
        self.builder.cbranch(condition, body_block, end_block)
        
        # Emit body
        self.builder.position_at_end(body_block)
        self.visit(node.body)
        self.builder.branch(cond_block)
        
        # Continue at end block
        self.builder.position_at_end(end_block)
    
    def visit_ForStmt(self, node: ForStmt) -> None:
        """Generate IR for a for statement."""
        self.logger.debug("Visiting for statement")
        # Create blocks
        preheader_block = self.builder.append_basic_block('for.preheader')
        cond_block = self.builder.append_basic_block('for.cond')
        body_block = self.builder.append_basic_block('for.body')
        increment_block = self.builder.append_basic_block('for.inc')
        end_block = self.builder.append_basic_block('for.end')
        self.builder.branch(preheader_block)
        self.builder.position_at_end(preheader_block)
        # Handle initializer (declaration or expression)
        if node.init:
            if isinstance(node.init, VariableDecl):
                self.visit_VariableDecl(node.init)
            else:
                self.visit(node.init)
        self.builder.branch(cond_block)
        self.builder.position_at_end(cond_block)
        # Condition
        if node.condition:
            cond_val = self.visit(node.condition)
            self.builder.cbranch(cond_val, body_block, end_block)
        else:
            self.builder.branch(body_block)
        # Body
        self.builder.position_at_end(body_block)
        self.visit(node.body)
        self.builder.branch(increment_block)        # Increment
        self.builder.position_at_end(increment_block)
        if node.increment:
            self.visit(node.increment)
        self.builder.branch(cond_block)
        # End
        self.builder.position_at_end(end_block)
    
    def visit_VariableDecl(self, node: VariableDecl) -> ir.Value:
        """Generate IR for a variable declaration."""
        self.logger.debug(f"Visiting variable declaration: {node.name}")
        
        # Create alloca instruction
        var_type = self.visit(node.type)
        
        # Track variable types for struct member access
        if not hasattr(self, 'variable_types'):
            self.variable_types = {}
        self.variable_types[node.name] = node.type.name
        
        ptr = self.builder.alloca(var_type, name=node.name)
        self.symbol_table[node.name] = ptr
        
        # Initialize if there's an initializer
        if node.init:
            init_val = self.visit(node.init)
            
            # Handle type conversions for assignments
            if var_type != init_val.type:
                # Handle float to double promotion
                if isinstance(var_type, ir.DoubleType) and isinstance(init_val.type, ir.FloatType):
                    init_val = self.builder.fpext(init_val, var_type)
                # Handle double to float demotion
                elif isinstance(var_type, ir.FloatType) and isinstance(init_val.type, ir.DoubleType):
                    init_val = self.builder.fptrunc(init_val, var_type)
                # Handle integer to float conversion
                elif isinstance(var_type, (ir.FloatType, ir.DoubleType)) and isinstance(init_val.type, ir.IntType):
                    init_val = self.builder.sitofp(init_val, var_type)
                # Handle float to integer conversion
                elif isinstance(init_val.type, (ir.FloatType, ir.DoubleType)) and isinstance(var_type, ir.IntType):
                    init_val = self.builder.fptosi(init_val, var_type)
            
            self.builder.store(init_val, ptr)
            
        return ptr
    
    def _convert_type(self, type_node: Type) -> ir.Type:
        """Convert AST type to LLVM type."""
        if type_node.name == 'void':
            return ir.VoidType()
        elif type_node.name == 'bool':
            return ir.IntType(1)
        elif type_node.name == 'char':
            return ir.IntType(8)
        elif type_node.name == 'short':
            return ir.IntType(16)
        elif type_node.name == 'int':
            return ir.IntType(32)
        elif type_node.name == 'long':
            return ir.IntType(64)
        elif type_node.name == 'float':
            return ir.FloatType()
        elif type_node.name == 'double':
            return ir.DoubleType()
        else:
            raise ValueError(f"Unknown type: {type_node.name}")
    
    def visit_StringLiteral(self, node: StringLiteral) -> ir.Value:
        """Generate IR for a string literal.
        
        Args:
            node: String literal node
            
        Returns:
            LLVM value representing the string constant
        """
        self.logger.debug(f"Visiting string literal: {node.value}")
        if not isinstance(node, StringLiteral):
            raise TypeError(f"Expected StringLiteral, got {type(node)}")
            
        # Ensure the value is a string and handle any escape sequences
        if not isinstance(node.value, str):
            raise TypeError(f"StringLiteral value must be a string, got {type(node.value)}")
            
        return self._create_string_constant(node.value)
    
    def get_pointer(self, node):
        # Helper to get the pointer for an identifier or dereference
        if isinstance(node, Identifier):
            var_name = node.name
            return self.symbol_table[var_name]
        elif isinstance(node, UnaryOp) and node.op == '&':
            # Address-of
            return self.visit(node.operand)
        elif isinstance(node, UnaryOp) and node.op == '*':
            # Dereference
            ptr = self.visit(node.operand)
            return self.builder.load(ptr)
        else:
            return self.visit(node)

    def visit_FunctionCall(self, node: FunctionCall) -> ir.Value:
        """Generate IR for a function call."""
        self.logger.debug(f"Visiting function call: {node.function}")
        if not isinstance(node, FunctionCall):
            raise TypeError(f"Expected FunctionCall, got {type(node)}")
        # Get the function
        if isinstance(node.function, Identifier) and node.function.name == "printf":
            func = self.printf_func
        else:
            func = self.module.get_global(node.function.name)
            if func is None:
                raise ValueError(f"Function {node.function.name} not found")
        # Generate IR for arguments, matching pointer types
        args = []
        for idx, arg in enumerate(node.arguments):
            if idx < len(func.args) and func.args[idx] is not None and isinstance(func.args[idx].type, ir.PointerType):
                # Pass pointer for pointer parameter
                if isinstance(arg, Identifier):
                    args.append(self.visit(arg, as_pointer=True))
                else:
                    args.append(self.visit(arg))
        return self.builder.call(func, args)
    
    def visit_IntegerLiteral(self, node: IntegerLiteral) -> ir.Constant:
        """Generate IR for an integer literal."""
        self.logger.debug(f"Visiting integer literal: {node.value}")
        if not isinstance(node, IntegerLiteral):
            raise TypeError(f"Expected IntegerLiteral, got {type(node)}")
        return ir.Constant(ir.IntType(32), node.value)
    
    def visit_FloatLiteral(self, node) -> ir.Constant:
        """Generate IR for a floating-point literal."""
        self.logger.debug(f"Visiting float literal: {node.value}")
        if not hasattr(node, 'value'):
            raise TypeError(f"Expected FloatLiteral with value, got {type(node)}")
        return ir.Constant(ir.FloatType(), float(node.value))
    
    def visit_DoubleLiteral(self, node) -> ir.Constant:
        """Generate IR for a double-precision floating-point literal."""
        self.logger.debug(f"Visiting double literal: {node.value}")
        return ir.Constant(ir.DoubleType(), float(node.value))
    
    def visit_ExpressionStmt(self, node: ExpressionStmt) -> None:
        """Generate IR for an expression statement."""
        self.logger.debug("Visiting expression statement")
        # Just visit the expression - its value will be discarded
        self.visit(node.expr)
    def visit_Type(self, node: Type) -> ir.Type:
        """Visit a type node."""
        self.logger.debug(f"Visiting type: {node.name}")
        base_type = None
        if node.name == 'int':
            base_type = ir.IntType(32)
        elif node.name == 'void':
            base_type = ir.VoidType()
        elif node.name == 'char':
            base_type = ir.IntType(8)
        elif node.name == 'float':
            base_type = ir.FloatType()
        elif node.name == 'double':
            base_type = ir.DoubleType()
        elif node.name.startswith('struct '):
            # Handle struct types with space
            struct_name = node.name[7:]  # Remove 'struct ' prefix
            if hasattr(self, 'struct_types') and struct_name in self.struct_types:
                base_type = self.struct_types[struct_name]['type']
            else:
                # Unknown struct type - create a placeholder
                base_type = ir.IntType(32)  # Default fallback
                self.logger.warning(f"Unknown struct type: {struct_name}")
        elif node.name.startswith('struct'):
            # Handle struct types without space (concatenated like "structPoint")
            struct_name = node.name[6:]  # Remove 'struct' prefix
            if hasattr(self, 'struct_types') and struct_name in self.struct_types:
                base_type = self.struct_types[struct_name]['type']
            else:
                # Unknown struct type - create a placeholder
                base_type = ir.IntType(32)  # Default fallback
                self.logger.warning(f"Unknown struct type: {struct_name}")
        elif hasattr(self, 'struct_types') and node.name in self.struct_types:
            # Direct struct type reference
            base_type = self.struct_types[node.name]['type']
        else:
            raise ValueError(f"Unsupported type: {node.name}")
        
        # Handle pointer types
        if getattr(node, 'is_pointer', False):
            return ir.PointerType(base_type)
        return base_type
    
    def get_ir(self) -> str:
        """Get the generated LLVM IR code.
        
        Returns:
            String containing LLVM IR code
        """
        return str(self.module)
    
    def visit_Constant(self, node) -> ir.Constant:
        """Generate IR for a constant (supports int, float, char, string)."""
        self.logger.debug(f"Visiting constant: {node.value} (type: {node.type})")
        if node.type == 'int':
            return ir.Constant(ir.IntType(32), int(node.value))
        elif node.type == 'float':
            return ir.Constant(ir.FloatType(), float(node.value))
        elif node.type == 'double':
            return ir.Constant(ir.DoubleType(), float(node.value))
        elif node.type == 'char':
            # Handle character constants
            if isinstance(node.value, str) and len(node.value) == 1:
                return ir.Constant(ir.IntType(8), ord(node.value))
            else:
                return ir.Constant(ir.IntType(8), int(node.value))
        elif node.type == 'string':
            # Handle string constants - delegate to StringLiteral logic
            return self._create_string_constant(str(node.value))
        else:
            # Default to integer
            return ir.Constant(ir.IntType(32), int(node.value))
    
    def visit_MemberAccess(self, node, as_pointer: bool = False) -> ir.Value:
        """Generate IR for member access."""
        self.logger.debug(f"Visiting member access: {node.base}.{node.member}")
        
        # Try to resolve base as a struct variable
        if hasattr(node.base, 'name') and node.base.name in self.symbol_table:
            base_ptr = self.symbol_table[node.base.name]
            
            # Check if we have struct type information for this variable
            if hasattr(self, 'struct_types') and hasattr(self, 'variable_types'):
                var_type = self.variable_types.get(node.base.name)
                if var_type:
                    # Handle different struct type name formats
                    struct_name = None
                    if var_type.startswith('struct '):
                        struct_name = var_type[7:]  # Remove 'struct ' prefix
                    elif var_type.startswith('struct'):
                        struct_name = var_type[6:]  # Remove 'struct' prefix (concatenated)
                    else:
                        struct_name = var_type  # Direct struct name
                    
                    if struct_name and struct_name in self.struct_types:
                        struct_info = self.struct_types[struct_name]
                        if node.member in struct_info['fields']:
                            # Generate GEP instruction for struct member access
                            field_index = struct_info['fields'][node.member]
                            member_ptr = self.builder.gep(base_ptr, [
                                ir.Constant(ir.IntType(32), 0),  # Dereference the struct pointer
                                ir.Constant(ir.IntType(32), field_index)  # Access the field
                            ])
                            
                            # Return pointer if requested, otherwise load the value
                            if as_pointer:
                                return member_ptr
                            else:
                                return self.builder.load(member_ptr)
        
        # Fallback to flattened variable approach for backward compatibility
        # Simple approach: concatenate base and member names
        if hasattr(node.base, 'name'):
            member_var_name = f"{node.base.name}_{node.member}"
        else:
            # Handle more complex base expressions
            member_var_name = f"temp_{id(node.base)}_{node.member}"
        
        # Check if this "flattened" variable exists
        if member_var_name in self.symbol_table:
            ptr = self.symbol_table[member_var_name]
            return self.builder.load(ptr)
        else:
            # Create the variable if it doesn't exist (for assignments)
            # Try to infer type from context - default to double for now
            var_type = ir.DoubleType()
            ptr = self.builder.alloca(var_type, name=member_var_name)
            self.symbol_table[member_var_name] = ptr
            
            # Initialize with zero
            zero = ir.Constant(var_type, 0.0)
            self.builder.store(zero, ptr)
            return self.builder.load(ptr)

# === STRUCT SUPPORT STUBS ===
# TODO: Map StructDecl to LLVM struct types
# TODO: Generate IR for struct allocation, member access, and assignment

    def visit_StructDecl(self, node):
        """Generate IR for struct declaration."""
        from frontend.ast.nodes import StructDecl
        
        if not isinstance(node, StructDecl):
            return None
        
        # Create LLVM struct type
        field_types = []
        for field in node.fields:
            if field.type.name == 'int':
                field_types.append(ir.IntType(32))
            elif field.type.name == 'float':
                field_types.append(ir.FloatType())
            elif field.type.name == 'double':
                field_types.append(ir.DoubleType())
            elif field.type.name == 'char':
                field_types.append(ir.IntType(8))
            else:
                # Default to int for unknown types
                field_types.append(ir.IntType(32))
        
        # Create the struct type
        struct_type = ir.LiteralStructType(field_types)
        
        # Store the struct type for later use
        if not hasattr(self, 'struct_types'):
            self.struct_types = {}
        self.struct_types[node.name] = {
            'type': struct_type,
            'fields': {field.name: i for i, field in enumerate(node.fields)},
            'field_types': {field.name: field.type.name for field in node.fields}
        }
        
        self.logger.debug(f"Created struct type: {node.name} with {len(node.fields)} fields")
        return None  # Struct declarations don't produce values

# === END STRUCT SUPPORT STUBS ===

# === TODO: FULL C IR GENERATION STUBS ===
# TODO: Generate IR for struct/union/enum/typedef
# TODO: Generate IR for arrays and pointer arithmetic
# TODO: Generate IR for all C control flow (for, while, do-while, switch, goto, break, continue)
# TODO: Generate IR for all C expressions (bitwise, logical, ternary, cast, sizeof, etc.)
# TODO: Generate IR for function pointers and variadic functions
# TODO: Generate IR for preprocessor directives (#include, #define, #ifdef, #ifndef, #endif)
# TODO: Generate IR for global/static/extern variables
# TODO: Generate IR for variable scoping and shadowing
# TODO: Generate IR for error handling and recovery
# === END FULL C IR GENERATION STUBS ===