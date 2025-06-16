from ir.ir_generator import IRGenerator
from frontend.ast.nodes import (
    TranslationUnit, FunctionDecl, Parameter, Type, CompoundStmt,
    ReturnStmt, BinaryOp, Identifier, IfStmt, BinaryOp, IntegerLiteral,
    FunctionCall
)

# Create AST for factorial function
param_n = Parameter("n", Type("int"))
factorial_params = [param_n]

# Create if condition: n <= 1
if_cond = BinaryOp(
    "<=",
    Identifier("n"),
    IntegerLiteral(1)
)

# If body: return 1
if_body = CompoundStmt([
    ReturnStmt(value=IntegerLiteral(1))
])

# Create recursive call: factorial(n - 1)
recursive_call = FunctionCall(
    Identifier("factorial"),
    [BinaryOp("-", Identifier("n"), IntegerLiteral(1))]
)

# Create return statement: return n * factorial(n - 1)
return_stmt = ReturnStmt(
    value=BinaryOp(
        "*",
        Identifier("n"),
        recursive_call
    )
)

# Create function body
factorial_body = CompoundStmt([
    IfStmt(if_cond, if_body, None),
    return_stmt
])

# Create factorial function declaration
factorial_decl = FunctionDecl(
    "factorial",
    Type("int"),
    factorial_params,
    factorial_body
)

# Create AST
ast = TranslationUnit([factorial_decl])

# Generate IR
generator = IRGenerator()
generator.visit(ast)  # First visit the AST to generate IR
print(str(generator.module))  # Then print the generated IR

def test_add_function():
    # Create a simple addition function
    param_a = Parameter("a", Type("int"))
    param_b = Parameter("b", Type("int"))
    add_params = [param_a, param_b]
    
    # Create return statement: return a + b
    return_stmt = ReturnStmt(
        value=BinaryOp(
            "+",
            Identifier("a"),
            Identifier("b")
        )
    )
    
    # Create function body
    add_body = CompoundStmt([return_stmt])
    
    # Create function declaration
    add_decl = FunctionDecl(
        "add",
        Type("int"),
        add_params,
        add_body
    )
    
    # Create AST
    tu = TranslationUnit([add_decl])
    
    # Generate IR
    generator = IRGenerator()
    generator.visit(tu)  # First visit the AST to generate IR
    print(str(generator.module))  # Then print the generated IR

if __name__ == "__main__":
    test_add_function() 